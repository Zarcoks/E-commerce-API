from models.shippingInformation import Shipping_Information
from playhouse.shortcuts import model_to_dict, dict_to_model

def hasAllDataForCreation(json_payload):
    return (
        "country" in json_payload
        and "address" in json_payload
        and "postal_code" in json_payload
        and "city" in json_payload
        and "province" in json_payload
    )


# Renvoie True si l'order contient tous les attributs liés à shipping info et email
# param order -> Model
def hasRegistredShippingInfo(order):
    dictOrder = model_to_dict(order)

    # Vérifie si shipping info est dans dictOrder, et que s'il y est, qu'il n'est pas None
    if (
        ("shipping_information" not in dictOrder) 
        or "shipping_information" in dictOrder and dictOrder["shipping_information"] is None):
        return False

    # Conversion du nom du modèle
    if ("postalCode" in dictOrder["shipping_information"]):
        dictOrder["shipping_information"]["postal_code"] = dictOrder["shipping_information"]["postalCode"]

    return (
        "email" in dictOrder and hasAllDataForCreation(dictOrder["shipping_information"])
    )


# Crée un shipping information selon celles données en paramètre
# Part du principe que les données ont été vérifiées
def createShippingInformation(json_payload):
    newShipInfo = Shipping_Information(
        country = json_payload["country"],
        address = json_payload["address"],
        postalCode = json_payload["postal_code"],
        city = json_payload["city"],
        province = json_payload["province"]
    )

    newShipInfo.save()

    return newShipInfo.id


# Calcule le shipping price selon comme demandé dans la consigne
def getShippingPrice(product, quantity):
    weight = product.weight * quantity
    if (weight < 500):
        return 500
    elif (weight < 2000):
        return 1000
    return 2500