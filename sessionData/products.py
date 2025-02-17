from flask import json
import requests

products = []


def gather_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

    products.extend(requests.get(url).json()['products'])