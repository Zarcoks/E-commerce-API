from models.transaction import Transaction
from playhouse.shortcuts import model_to_dict, dict_to_model


def createTransaction(json_payload):
    print(json_payload)
    newTransaction = Transaction(
        api_id = json_payload["id"],
        success = json_payload["success"] == 'true',
        amount_charged = json_payload["amount_charged"]
    )
    print(model_to_dict(newTransaction))
    newTransaction.save()

    return newTransaction.id
