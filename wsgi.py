# wsgi.py
# Carlos Valdez
#
# This is where the website begins.

from src.app import app

if __name__ == '__main__':
    app.run()
