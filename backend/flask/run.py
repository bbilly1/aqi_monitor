"""

Documentation: https://flask.palletsprojects.com

Install on Arch
- sudo pacman -S python-flask
- sudo pacman -S python-flask-httpauth

or with pip
- pip install Flask
- pip install Flask-HTTPAuth


Run Debug env:
export FLASK_APP=run.py
export FLASK_DEBUG=1

"""


from app import app



if __name__ == "__main__":
    app.run()
