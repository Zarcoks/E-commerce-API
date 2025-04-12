from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from controllers import product_blp, order_blp
from db import db
from data_loader import gather_products
from rq import Worker, Queue, Connection
from .services.redis_config import redis_client
from flask.cli import AppGroup
import models


app = Flask(__name__)

worker_cli = AppGroup('worker')

app.register_blueprint(product_blp, url_prefix='/')
app.register_blueprint(order_blp, url_prefix='/')

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([
        models.Credit_Card, 
        models.Order, 
        models.Product, 
        models.Product_Command, 
        models.OrderProduct, 
        models.Shipping_Information, 
        models.Transaction
    ], safe=True)
    db.close()
    gather_products()


@app.cli.command('worker')
def run_worker():
    with Connection(redis_client):
        worker = Worker(['default'])
        worker.work()