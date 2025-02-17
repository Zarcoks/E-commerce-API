from db import db
import peewee as p

class BaseModel(p.Model):
    class Meta:
        database = db
