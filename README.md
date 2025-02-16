To setup your environment without docker:

python3 -m venv .venv

On VSCode:
Ctrl + Shift + P
Python: Select Interpreter

Then select the one where you'll see ".env" in it. 

This will allow you to run a python virtual environment, in which you'll be able to run:

flask run


Alternatively, for docker usage, just run the following:

docker build -t flask-tp .

docker run -d -p 3000:3000 flask-tp

Make sure you installed docker first !
