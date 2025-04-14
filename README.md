Création du virtual environment:
py -3 -m venv .venv

Sur VSCode: 
Ctrl + Shift + P
Python: Select Interpreter
Sélectionner celui où il y de noté ".venv"

Puis installer les requirements:
pip install -r requirements.txt


NE PAS OUBLIER DE CREER LA DB
flask init-db


Le projet suit la structure MVCS (Model - View - Controller - Service)

Pour la communication entre les controleurs et les services, j'avais besoin d'une gestion d'erreur personnalisable. Pour répondre à ce problème j'ai préféré faire simple et utiliser un dictionnaire pour chaque fonction de service qui soit appelée par un controleur. Ainsi je peux communiquer un code http, et une erreur si besoin. 


A ne pas tenir compte:
Lancer l'app: 
> docker compose up -d --build
> flask init-db
> flask worker

docker build -t rest-apis-flask-python .
docker run -d -p 5000:5000 rest-apis-flask-python

TODO: Faire en sorte qu'après une erreur de carte de crédit, on puisse renvoyer une bonne carte et que ça formate tout comme il faut