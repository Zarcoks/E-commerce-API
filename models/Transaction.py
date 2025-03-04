import datetime
from .BaseModel import BaseModel
import peewee as p

class Transaction(BaseModel):
    id = p.CharField(primary_key=True)
    success = p.BooleanField(),
    amount_charged = p.IntegerField()