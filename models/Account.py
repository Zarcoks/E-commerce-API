from .BaseModel import BaseModel
import peewee as p

class Account(BaseModel):
    id = p.AutoField(primary_key=True)
    owner = p.CharField(unique=True, null=False)
    current_balance = p.IntegerField(default=0, constraints=[
        p.Check('current_balance >= 0')
    ])