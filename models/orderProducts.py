from .BaseModel import BaseModel
from models.product import Product
from models.order import Order
import peewee as p

class OrderProduct(BaseModel):
    order = p.ForeignKeyField(Order, backref='order_products')
    product = p.ForeignKeyField(Product, backref='product_orders')
    quantity = p.IntegerField()