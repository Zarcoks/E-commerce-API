import datetime
from .BaseModel import BaseModel
from .Account import Account
import peewee as p

class Transaction(BaseModel):
    id = p.AutoField(primary_key=True)
    from_account = p.ForeignKeyField(Account, backref="transactions_from", null=False)
    to_account = p.ForeignKeyField(Account, backref="transactions_to", null=False)
    timestamp = p.DateTimeField(default=datetime.datetime.now)
    amount = p.IntegerField(constraints=[
        p.Check('amount > 0')
    ])