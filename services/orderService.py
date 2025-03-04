from models.order import Order
from models.product import Product
from models.productCommand import Product_Command
from .shippingInformationService import hasAllDataForCreation, createShippingInformation
from .generalService import resDict 
from playhouse.shortcuts import model_to_dict, dict_to_model


# Calcule le shipping price selon comme demandé dans la consigne
def getShippingPrice(product):
    weight = product.price
    if (weight < 500):
        return 5.0
    elif (weight < 2000):
        return 10.0
    return 25.0


# Prend le payload de la commande, et renvoie l'id de la nouvelle commande
def createOrder(json_payload):
    if (json_payload is None or "id" not in json_payload or "quantity" not in json_payload):
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
        total_price=product.price * json_payload["quantity"],
        shipping_price=getShippingPrice(product),
        product=new_product_order
    )

    new_order.save()

    return resDict(new_order.id, 302, False)


# Remplace les champs null par des dict vides pour des colonnes données
# "credit_card": null  ---->  "credit_card": {}
def formatOrder(order):
    del order["product"]["product_id"] # Join automatique de peewee
    
    # Champs concernés
    to_replace = ["credit_card", "shipping_information", "transaction"]

    for replaceKey in to_replace:
        if (order[replaceKey] is None):
            order[replaceKey] = {}
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


# Modifie l'order d'id orderId avec les infos dans json_payload (seulement celles définies dans la consigne)
def addUserInfoToOrder(orderId, json_payload):
    if (json_payload is None or "email" not in json_payload 
        or "shipping_information" not in json_payload
        or hasAllDataForCreation(json_payload["shipping_information"])):
        return resDict(-1, 422, True, {
            "errors" : {
                "order": {
                    "code": "missing-fields",
                    "name": "Il manque un ou plusieurs champs qui sont obligatoires",
                }
            }
        })
    
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