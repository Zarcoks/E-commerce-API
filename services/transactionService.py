from models.Transaction import Transaction
from playhouse.shortcuts import model_to_dict, dict_to_model


def createTransaction(json_payload):
    newTransaction = Transaction(
        api_id = json_payload["id"],
        success = json_payload["success"] == 'true',
        amount_charged = json_payload["amount_charged"]
    )
    
    newTransaction.save()

    return newTransaction.id
