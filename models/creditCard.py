from .BaseModel import BaseModel
import peewee as p

class Credit_Card(BaseModel):
    id = p.AutoField(primary_key=True)
    name = p.CharField(null=False)
    first_digits = p.CharField(null=False)
    last_digits = p.CharField(null=False)
    expiration_year = p.IntegerField()
    expiration_month = p.IntegerField()
