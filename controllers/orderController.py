from flask import Blueprint, abort, jsonify, redirect, request, url_for
from models import Order, Product, Product_Command
from playhouse.shortcuts import model_to_dict, dict_to_model
import peewee as p
from services import createOrder, addUserInfoToOrder, getOrder, modifyOrder


order_blp = Blueprint('order_blp', __name__)


@order_blp.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    res = getOrder(id)

    if (res["hasError"]):
        return jsonify(res["result"]), res["code"]
    return jsonify(res["result"]), res["code"]


@order_blp.route('/order', methods=["POST"])
def create_order():
    if not request.is_json:
        return abort(400)

    if ("product" in request.json):
        json_payload = request.json['product']
    elif ("products" in request.json):
        json_payload = request.json['products']
    else:
        json_payload = None

    res = createOrder(json_payload)

    if (res["hasError"]):
        return jsonify(res["error"]), res["code"]
    else:
        return jsonify(), 302, {'location': '/order/' + str(res["result"])}



@order_blp.route('/order/<int:order_id>', methods=["PUT"])
def modify_order(order_id):
    if not request.is_json:
        return abort(400)

    if ("order" in request.json):
        json_payload = request.json['order']
    elif ("credit_card" in request.json):
        json_payload = {"credit_card": request.json["credit_card"]}
    else:
        json_payload = None

    res = modifyOrder(order_id, json_payload)

    if (res["hasError"]):
        return jsonify(res["error"]), res["code"]

    return get_order(res["result"]["id"])


#TEMP
@order_blp.route('/product_command', methods=['GET'])
def get_products():
    try:
        # Récupérer tous les Product_Command depuis la base de données
        products = Product_Command.select()

        # Convertir les objets en dictionnaires
        product_list = [model_to_dict(product) for product in products]

        return jsonify(product_list), 200

    except Exception as e:
        return jsonify({"message": f"Erreur lors de la récupération des produits : {str(e)}"}), 500
