import json
from flask import jsonify
import requests
import urllib
from models.product import Product


def gather_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

    # Récupération des données via urllib.request
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')
        products = json.loads(data)['products']

    # Création des produits
    for product in products:
        Product.create(
            id=product["id"],
            name=product["name"],
            in_stock=product["in_stock"],
            description=product["description"],
            price=product["price"],
            weight=product["weight"],
            image=product["image"]
        )