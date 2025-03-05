from .BaseModel import BaseModel
import peewee as p

class Transaction(BaseModel):
    id = p.AutoField(primary_key=True)
    api_id = p.CharField()
    success = p.BooleanField()
    amount_charged = p.IntegerField()