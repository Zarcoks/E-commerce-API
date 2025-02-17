from flask import Blueprint, abort, jsonify, redirect, request, url_for
from models import Product
from playhouse.shortcuts import model_to_dict, dict_to_model


product_blp = Blueprint('product_blp', __name__)

@product_blp.route('/products', methods=['GET'])
def products():
    products = []
    for account in Product.select():
        products.append(model_to_dict(account))

    return jsonify(products)