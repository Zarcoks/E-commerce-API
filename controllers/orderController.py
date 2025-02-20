from flask import Blueprint, abort, jsonify, redirect, request, url_for
from models import Order, Product, Product_Command
from playhouse.shortcuts import model_to_dict, dict_to_model
import peewee as p
from services import getShippingPrice


order_blp = Blueprint('order_blp', __name__)


@order_blp.route('/order/<int:id>', methods=['GET'])
def get_order(id):
    order = model_to_dict(Order.get_by_id(id))

    return jsonify(order)


@order_blp.route('/order', methods=["POST"])
def create_order():
    if not request.is_json:
        return abort(400)

    json_payload = request.json['product']

    new_product_order = Product_Command(
        product_id=json_payload["id"],
        quantity=json_payload["quantity"]
    )

    new_product_order.save()

    product = Product.get_by_id(json_payload["id"])

    # Créer une nouvelle commande avec les champs spécifiés
    new_order = Order(
        total_price=product.price * json_payload["quantity"],
        shipping_price=getShippingPrice(product),
        product=new_product_order
    )

    # Sauvegardez la nouvelle commande dans la base de données
    new_order.save()

    return redirect(url_for('order_blp.get_order', id=new_order.id), code=302)


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
