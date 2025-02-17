"""
from flask import Blueprint, abort, jsonify, redirect, request, url_for
from models import Account, Transaction
from playhouse.shortcuts import model_to_dict, dict_to_model
import peewee as p

account_blp = Blueprint('account_blp', __name__)

@account_blp.route('/accounts', methods=['GET'])
def accounts():
    accounts = []
    for account in Account.select():
        accounts.append(model_to_dict(account))

    return jsonify(accounts)


@account_blp.route('/accounts/<int:id>', methods=['GET'])
def accounts_get(id):
    account = Account.get_or_none(id)
    if account is None:
        return abort(404)

    return jsonify(model_to_dict(account))


@account_blp.route('/accounts/<int:id>/transactions', methods=['GET'])
def accounts_transactions(id):
    account = Account.get_or_none(id)
    if account is None:
        return abort(404)

    transactions = []
    for transaction in account.transactions_from:
        transactions.append(model_to_dict(transaction))

    for transaction in account.transactions_to:
        transactions.append(model_to_dict(transaction))

    return jsonify(transactions)


@account_blp.route('/accounts/<int:id>/transactions/<int:transaction_id>', methods=['GET'])
def accounts_transactions_get(id, transaction_id):
    transaction = Transaction.get_or_none(Transaction.id == transaction_id)
    if transaction is None:
        return abort(404)

    if transaction.to_account.id == id or transaction.from_account.id == id:
        return jsonify((model_to_dict(transaction)))

    return abort(404)


@account_blp.route('/accounts', methods=['POST'])
def accounts_create():
    if not request.is_json:
        return abort(400)

    json_payload = request.json['account']
    json_payload['id'] = None

    new_account = dict_to_model(Account, json_payload)

    try:
        new_account.save()
    except p.IntegrityError:
        return jsonify({
            "error": "Un compte avec le même propriétaire existe déjà"
        }), 422

    return redirect(url_for("accounts_get", id=new_account.id))
"""