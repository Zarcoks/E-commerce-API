Lancer l'app: 
1. docker compose up -d --build
2. flask init-db
3. flask worker


Veiller à lancer les commandes flask à l'intérieur du conteneur, sinon ça ne va pas marcher.

Pour lancer le frontend, il suffit de lancer index.html qui vous redirigera sur ./frontend/index.html qui contient donc le véritable frontend, en ayant bien sûr préalablement lancé l'API. 


Auteur:
Victor JOST (JOSV14080400)