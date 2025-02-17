from .BaseModel import BaseModel
from .product import Product
import peewee as p

class Product_Command(BaseModel):
    id = p.AutoField(primary_key=True)
    product_id = p.ForeignKeyField(Product, backref="product_id", null=False)
    quantity = p.IntegerField(constraints=[
        p.Check('quantity >= 1')
    ])