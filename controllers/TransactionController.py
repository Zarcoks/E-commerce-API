from flask import Blueprint, abort, jsonify, redirect, request, url_for
import db
from models import Account, Transaction
from playhouse.shortcuts import model_to_dict, dict_to_model
import peewee as p

transaction_blp = Blueprint("transaction_blp", __name__)

@transaction_blp.route('/transactions', methods=['POST'])
def transactions_create():
    if not request.is_json:
        return abort(400)

    json_payload = request.json['transaction']
    json_payload['id'] = None

    new_transaction = dict_to_model(Transaction, json_payload)
    with db.atomic() as transaction:
        try:
            new_transaction.save()

            Account.update(
                current_balance = Account.current_balance - new_transaction.amount
            ).where(Account.id == new_transaction.from_account.id).execute()

            Account.update(
                current_balance = Account.current_balance + new_transaction.amount
            ).where(Account.id == new_transaction.to_account.id).execute()

            transaction.commit()
        except Account.DoesNotExist:
            transaction.rollback()

            return jsonify({
                "error": {
                    "code": "account-not-found",
                    "text": "Un des comptes n'existe pas"
                }
            }), 422
        except p.IntegrityError:
            return jsonify({
                "error": {
                    "code": "insuffisant-funds",
                    "error": "Fonds insuffisants",
                }
            }), 422
        except:
            transaction.rollback()
            return abort(400)

    return redirect(url_for("transactions_get", id=new_transaction.id))


@transaction_blp.route('/transactions/<int:id>', methods=['GET'])
def transactions_get(id):
    transaction = Transaction.get_or_none(id)
    if transaction is None:
        return abort(404)

    return jsonify(model_to_dict(transaction))
