from models.transaction import Transaction
from playhouse.shortcuts import model_to_dict, dict_to_model


def createTransaction(json_payload):
    newTransaction = Transaction(
        api_id = json_payload["id"],
        success = json_payload["success"] == 'true',
        amount_charged = json_payload["amount_charged"]
    )
    
    newTransaction.save()

    return newTransaction.id


def createErrorTransaction(apiError):
    print(apiError)
    name, code = apiError["errors"]["credit_card"]["name"], apiError["errors"]["credit_card"]["code"]
    newTransaction = Transaction(
        success = False,
        error_code = code,
        error_name = name
    )

    newTransaction.save()

    return newTransaction.id

def filterTransactionFields(transaction):
    if (transaction["success"]):
        del transaction["error_code"]
        del transaction["error_name"]
    return transaction