from flask import Flask
from controllers import account_blp, transaction_blp
from db import db
import models


app = Flask(__name__)

app.register_blueprint(account_blp, url_prefix='/api')
app.register_blueprint(transaction_blp, url_prefix='/api')

@app.cli.command("init-db")
def init_db():
    db.connect()
    db.create_tables([models.Account, models.Transaction], safe=True)  # safe=True évite les erreurs si les tables existent déjà
    db.close()
