from models.transaction import Transaction

def createTransaction(json_payload):
    newTransaction = Transaction(
        id = json_payload["id"],
        success = json_payload["success"],
        amount_charged = json_payload["amount_charged"]
    )

    newTransaction.save()

    return newTransaction.id