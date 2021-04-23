import os
from api import app
from werkzeug.contrib.fixers import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app)
application = app

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
