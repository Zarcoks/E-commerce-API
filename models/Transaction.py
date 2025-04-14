from .BaseModel import BaseModel
import peewee as p

class Transaction(BaseModel):
    id = p.AutoField(primary_key=True)
    api_id = p.CharField(null=True)
    success = p.BooleanField()
    amount_charged = p.IntegerField(null=True)
    error_code = p.CharField(null=True)
    error_name = p.CharField(null=True)