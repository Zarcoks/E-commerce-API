from models.shippingInformation import Shipping_Information

def hasAllDataForCreation(json_payload):
    return (
        "country" not in json_payload
        or "address" not in json_payload
        or "postal_code" not in json_payload
        or "city" not in json_payload
        or "province" not in json_payload
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