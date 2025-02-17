import requests
from models.product import Product


def gather_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

    products = requests.get(url).json()['products']

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