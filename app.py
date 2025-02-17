from flask import Flask
from controllers import account_blp, transaction_blp, product_blp
from db import db
from data_loader import gather_products
import models
from models.product import Product


app = Flask(__name__)

app.register_blueprint(product_blp, url_prefix='/api')

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([models.Account, models.Transaction, Product], safe=True)
    db.close()
    gather_products()
