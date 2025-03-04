from models.creditCard import Credit_Card


def hasAllDataForCreation(json_payload):
    return ("credit_card" in json_payload
          and "name" in json_payload["credit_card"]
          and "number" in json_payload["credit_card"]
          and "expiration_year" in json_payload["credit_card"]
          and "cvv" in json_payload["credit_card"]
          and "expiration_month" in json_payload["credit_card"])


def createCreditCard(json_payload):
    newCreditCard = Credit_Card(
        name = json_payload["name"],
        first_digits = json_payload["first_digits"],
        last_digits = json_payload["last_digits"],
        expiration_year = json_payload["expiration_year"],
        expiration_month = json_payload["expiration_month"]
    )

    newCreditCard.save()

    return newCreditCard.id