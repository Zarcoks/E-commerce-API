from .BaseModel import BaseModel
import peewee as p

class Product(BaseModel):
    id = p.AutoField(primary_key=True)
    name = p.CharField(null=False)
    in_stock = p.BooleanField(null=False)
    description = p.CharField(null=False)
    price = p.FloatField(null=False) #constraints="price > 0" maybe? 
    weight = p.IntegerField(null=False) #constraints="price > 0" maybe? 
    image = p.CharField(null=False)