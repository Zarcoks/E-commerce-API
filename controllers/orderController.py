from flask import Blueprint, abort, jsonify, redirect, request, url_for
from models import Order, Product, Product_Command
from playhouse.shortcuts import model_to_dict, dict_to_model


order_blp = Blueprint('order_blp', __name__)

@order_blp.route('/orders', methods=['GET'])
def get_orders():
    orders = []
    for account in Order.select():
        orders.append(model_to_dict(account))

    return jsonify(orders)


@order_blp.route('/order', methods=["POST"])
def create_order():
    if not request.is_json:
        return abort(400)

    json_payload = request.json['product']
    #print("json_payload: ", json_payload['id'])

    pass