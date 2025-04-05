import json
import urllib
from models.product import Product

def clean_string(s):
    if isinstance(s, str):
        return s.replace('\x00', '').strip()
    return s  # Ne touche pas si ce n’est pas une string

def gather_products():
    url = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

    # Récupération des données via urllib.request
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')
        products = json.loads(data)['products']

    # Création des produits
    for product in products:
        try:
            Product.create(
                id=product["id"],
                name=clean_string(product["name"]),
                in_stock=product["in_stock"],
                description=clean_string(product["description"]),
                price=product["price"],
                weight=product["weight"],
                image=clean_string(product["image"])
            )
        except Exception as e:
            print(f"Erreur lors de l’insertion du produit {product['id']}: {e}")
