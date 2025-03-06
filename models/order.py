from .BaseModel import BaseModel
from models.shippingInformation import Shipping_Information
from models.productCommand import Product_Command
from models.creditCard import Credit_Card
from models.Transaction import Transaction
import peewee as p

class Order(BaseModel):
    id = p.AutoField(primary_key=True)
    email = p.CharField(null=True)
    total_price = p.FloatField()
    total_price_tax = p.FloatField(null=True)
    paid = p.BooleanField(default=False)
    shipping_price = p.FloatField()
    shipping_information = p.ForeignKeyField(Shipping_Information, backref="shipping_information", null=True)
    product = p.ForeignKeyField(Product_Command, backref="product", null=False)
    credit_card = p.ForeignKeyField(Credit_Card, backref="credit_card", null=True)
    transaction = p.ForeignKeyField(Transaction, backref="transaction", null=True)
    