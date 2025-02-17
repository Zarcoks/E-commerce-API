from .BaseModel import BaseModel
import peewee as p

class Shipping_Information(BaseModel):
    id = p.AutoField(primary_key=True)
    country = p.CharField(null=False)
    address = p.CharField(null=False)
    postalCode = p.CharField(null=False)
    city = p.CharField(null=False)
    province = p.CharField(null=False)