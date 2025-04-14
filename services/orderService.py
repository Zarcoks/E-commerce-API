import json

import urllib
from models.order import Order
from models.product import Product
from models.productCommand import Product_Command
from models.orderProducts import OrderProduct
from .shippingInformationService import *
from .creditCardService import hasAllDataForCreation as hasAllDataForCreditCardCreation, createCreditCard
from .transactionService import createTransaction, createErrorTransaction
from .generalService import resDict 
from playhouse.shortcuts import model_to_dict, dict_to_model
from redis import Redis
from redis import RedisError
from .redis_config import redis_client
from rq import Queue
from .QueueConnection import queue

def serialize_order(order):
    return json.dumps({
        "id": order["id"],
        "email": order["email"],
        "total_price": order["total_price"],
        "total_price_tax": order["total_price_tax"],
        "paid": order["paid"],
        "shipping_price": order["shipping_price"],
        "shipping_information": order["shipping_information"]["id"] if order["shipping_information"] else None,
        "credit_card": order["credit_card"]["id"] if order["credit_card"] else None,
        "transaction": order["transaction"]["id"] if order["transaction"] else None,
    })

def deserialize_order(order_json):
    return json.loads(order_json)

def getOneOrderError(json_payload):
    if (json_payload is None 
        or "id" not in json_payload 
        or "quantity" not in json_payload
        or json_payload["quantity"] < 1):
        return resDict(-1, 422, True, {
            "errors": {
                "product": {
                    "code": "missing-fields",
                    "name": "La création d'une commande nécessite un produit"
                }
            }})

    try:
        product = Product.get_by_id(json_payload["id"])
    except:
        return resDict(-1, 404, True, {}) # non demandé
    
    if (not product.in_stock):
        return resDict(-1, 422, True, {
            "errors" : {
                "product": {
                    "code": "out-of-inventory",
                    "name": "Le produit demandé n'est pas en inventaire"
                }
            }
        })
    return resDict(0, 200)


def calculateTotalPrice(products):
    totalPrice = 0
    for product in products:
        p = model_to_dict(product)
        totalPrice += p["product"]["price"] * p["quantity"] * 100
    return totalPrice

# Prend le payload de la commande, et renvoie l'id de la nouvelle commande
def createOrder(json_payload):
    if not isinstance(json_payload, list):
        json_payload = [json_payload]

    new_order = Order()

    new_order.save()

    products = []

    for product in json_payload:
        # Vérification de chaque produit
        error = getOneOrderError(product)
        if (error["hasError"]): return error

        products.append(OrderProduct(
            order = new_order.id,
            product = product["id"],
            quantity = product["quantity"]
        ))

    for verifiedProduct in products:
        verifiedProduct.save()

    new_order.total_price = calculateTotalPrice(products)
    new_order.shipping_price = getShippingPrice(products)
    new_order.save()

    return resDict(new_order.id, 302)



# Remplace les champs null par des dict vides pour des colonnes données
# "credit_card": null  ---->  "credit_card": {}
def formatOrder(order, products):

    # Champs concernés
    to_replace = ["credit_card", "shipping_information", "transaction"]

    for replaceKey in to_replace:
        if (order[replaceKey] is None):
            order[replaceKey] = {}

    # On remplace l'id de l'objet transaction par l'id de la transaction de l'api de paiement 
    if ("id" in order["transaction"] and "api_id" in order["transaction"]):
        del order["transaction"]["id"]
        del order["transaction"]["api_id"]

        if (not order["transaction"]["success"]):
            error = {
                "code": order["transaction"]["error_code"],
                "name": order["transaction"]["error_name"]
            }
            order["transaction"]["amount_charged"] = 0
            order["transaction"]["error"] = error
            del order["transaction"]["error_code"]
            del order["transaction"]["error_name"]
    
    if ("shipping_information" in order 
        and order["shipping_information"] is not None
        and "id" in order["shipping_information"]):
        del order["shipping_information"]["id"]
    


    order["products"] = []
    for product in products:
        order["products"].append({
            "id": product["product"]["id"],
            "quantity": product["quantity"]
        })

    return order


# Renvoie une order si trouvée
# Renvoie un 404 si la commande n'a pas été trouvée
def getOrder(id):
    try:
        if redis_client.exists(f"order:{id}:processing"):
            return resDict(None, 202)
        # Récupération depuis redis si possible:
        cached_order = redis_client.get(f"order:{id}")
        if cached_order:
            order = dict_to_model(model_class=Order, data=deserialize_order(cached_order))
        else: order = Order.get_by_id(id)
        products = []
        for product in OrderProduct.select(OrderProduct).where(OrderProduct.order == order.id):
            products.append(model_to_dict(product))
    except:
        return resDict({}, 404, True)
    
    order = model_to_dict(order)
    order = formatOrder(order, products)
    
    return resDict(order, 200)


# Met à jour total_price_tax, en supposant l'existance de shippingPrice
def updateOrder(order, province):
    taxes = {
        "QC": 1.15,
        "ON": 1.13,
        "AB": 1.05,
        "BC": 1.12,
        "NS": 1.14
    }

    # Oubli volontaire de la vérification des provinces 
    order.total_price_tax = order.total_price * taxes[province]
    return order


# Vérifie les données utilisateur et redirige vers la fonction de modification nécessaire
def modifyOrder(orderId, json_payload):
    missingFields = resDict(-1, 422, True, {
                "errors" : {
                    "order": {
                        "code": "missing-fields",
                        "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                    }
                }
            })
    
    if (json_payload is None):
        return missingFields
    
    # Queue du worker
    if redis_client.exists(f"order:{orderId}:processing"):
        return resDict(-1, 409, True, {})
    
    # S'il s'agit d'une modification à propos de shipping information et email:
    if ("email" in json_payload 
        and "shipping_information" in json_payload
        and hasAllDataForCreation(json_payload["shipping_information"])):
        return addUserInfoToOrder(orderId, json_payload)
    
    # S'il s'agit d'une modification à propos de credit card
    elif (hasAllDataForCreditCardCreation(json_payload)):
        # Pose un flag de traitement en cours
        redis_client.set(f"order:{orderId}:processing", "1")
        queue.enqueue(processPayment, orderId, json_payload, job_timeout=None)
        return resDict(None, 202)

    return missingFields


def processPayment(orderId, json_payload):
    rep = addCreditCardToOrder(orderId, json_payload)
    order = rep["result"]

    if not rep["hasError"] and order["paid"]:
        try:
            redis_client.set(f"order:{orderId}", serialize_order(order))
        except RedisError as e:
            print(f"Erreur lors de la mise en cache Redis: {e}")

    redis_client.delete(f"order:{orderId}:processing")

# Renvoie un resDict avec l'erreur associée si erreur il y a, sinon un resDict vide sans erreur
def verifyDataBeforePayment(order):
    # Erreur si commande déjà payée
    if (order.paid):
        return resDict(-1, 422, True, {
            "errors" : {
                "order": {
                    "code": "already-paid",
                    "name": "La commande a déjà été payée."
                }
            }
        })
    
    # Erreur si la commande n'a pas de shipping info / email
    elif (not hasRegistredShippingInfo(order)):
        return resDict(-1, 422, True, {
            "errors" : {
                "order": {
                    "code": "missing-fields",
                    "name": "Les informations du client sont nécessaire avant d'appliquer une carte de crédit"
                }
            }
        })
    
    return resDict(0, 200)

def addCreditCardToOrder(orderId, json_payload):
    # Récupération de l'order
    try:
        order = Order.get_by_id(orderId)
    except:
        return resDict(-1, 404, True, {})
    
    # Vérification des data
    resVerif = verifyDataBeforePayment(order)
    if (resVerif["hasError"]):
        return resVerif
    
    # Application du paiement
    json_payload["amount_charged"] = order.total_price_tax + order.shipping_price
    apiResponse = sendPaymentData(json_payload)
    
    if (not apiResponse["hasError"]):
        # Update si le paiement a réussi
        paymentData = apiResponse["result"]
        order.credit_card = createCreditCard(paymentData["credit_card"])
        order.transaction = createTransaction(paymentData["transaction"])
        order.paid = True

    order.transaction = createErrorTransaction(apiResponse["error"])
    
    order.save()
    return resDict(model_to_dict(order), 200)
        

# Modifie l'order d'id orderId avec les infos dans json_payload (seulement celles définies dans la consigne)
# Suppose les données déjà vérifiées
def addUserInfoToOrder(orderId, json_payload):
    try:
        order = Order.get_by_id(orderId)
    except:
        return resDict(-1, 404, True, {})

    shippingId = createShippingInformation(json_payload["shipping_information"])
    order.email = json_payload["email"]
    order.shipping_information = shippingId
    order = updateOrder(order, json_payload["shipping_information"]["province"])
    order.save()

    return resDict(model_to_dict(order), 200)


# Renvoie le json des data renvoyées par l'API de paiement
def sendPaymentData(payload):
    url = "https://dimensweb.uqac.ca/~jgnault/shops/pay/"
    headers = {"Content-Type": "application/json"}
    
    # Préparation de la requête
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))

        if response_data and "errors" in response_data:
            return resDict(-1, response.getcode(), True, response_data)  # Carte déclinée
    
    # Erreur de l'API distante
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
        except:
            error_data = {"error": "Unknown error occurred"}
        return resDict(-1, e.code, True, error_data)

    except Exception as e:
        # Erreur de connexion ou autre problème
        return resDict(-1, 500, True, {"error": str(e)})
    
    
    return resDict(response_data, response.getcode())  # Cas où ça a marché