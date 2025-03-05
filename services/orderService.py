from models.order import Order
from models.product import Product
from models.productCommand import Product_Command
from .shippingInformationService import *
from .creditCardService import hasAllDataForCreation as hasAllDataForCreditCardCreation, createCreditCard
from .transactionService import createTransaction
from .generalService import resDict 
from playhouse.shortcuts import model_to_dict, dict_to_model
import requests


# Prend le payload de la commande, et renvoie l'id de la nouvelle commande
def createOrder(json_payload):
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

    new_product_order = Product_Command(
        product_id=json_payload["id"],
        quantity=json_payload["quantity"]
    )

    new_product_order.save()

    new_order = Order(
        total_price=product.price * 100 * json_payload["quantity"], # cout en centimes
        shipping_price=getShippingPrice(product, json_payload["quantity"]),
        product=new_product_order
    )

    new_order.save()

    return resDict(new_order.id, 302, False)


# Remplace les champs null par des dict vides pour des colonnes données
# "credit_card": null  ---->  "credit_card": {}
def formatOrder(order):
    order["product"]["id"] = order["product"]["product_id"]["id"]
    del order["product"]["product_id"] # Join automatique de peewee

    
    # Champs concernés
    to_replace = ["credit_card", "shipping_information", "transaction"]

    for replaceKey in to_replace:
        if (order[replaceKey] is None):
            order[replaceKey] = {}

    # On remplace l'id de l'objet transaction par l'id de la transaction de l'api de paiement 
    if ("id" in order["transaction"] and "api_id" in order["transaction"]):
        order["transaction"]["id"] = order["transaction"]["api_id"]
        del order["transaction"]["api_id"]

    return order


# Renvoie une order si trouvée
# Renvoie un 404 si la commande n'a pas été trouvée
def getOrder(id):
    try:
        order = Order.get_by_id(id)
    except:
        return resDict({}, 404, True)
    
    order = model_to_dict(order)
    order = formatOrder(order)
    
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
    
    # S'il s'agit d'une modification à propos de shipping information et email:
    if ("email" in json_payload 
        and "shipping_information" in json_payload
        and hasAllDataForCreation(json_payload["shipping_information"])):
        return addUserInfoToOrder(orderId, json_payload)
    
    # S'il s'agit d'une modification à propos de credit card
    elif (hasAllDataForCreditCardCreation(json_payload)):
        return addCreditCardToOrder(orderId, json_payload)

    return missingFields
        

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
    
    if (apiResponse["hasError"]):
        return apiResponse # erreur lors du paiement
    else:
        # Update si le paiement a réussi
        paymentData = apiResponse["result"]
        order.credit_card = createCreditCard(paymentData["credit_card"])
        order.transaction = createTransaction(paymentData["transaction"])
        order.paid = True
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
    
    response = requests.post(url, json=payload, headers=headers)
    
    try:
        response_data = response.json()
    except:
        response_data = None # Erreur de l'API distante

    if ("errors" in response_data):
        return resDict(-1, response.status_code, True, response_data) # Carte déclinée
    
    return resDict(response_data, response.status_code) # Cas où ça a marché