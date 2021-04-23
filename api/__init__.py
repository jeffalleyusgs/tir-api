from dotenv import load_dotenv, find_dotenv
from flask import Flask, Blueprint, Request, url_for, send_from_directory
from flask_restx import Api, Resource
from flask_restx.apidoc import apidoc
from flask_cors import CORS
import os
import time

load_dotenv(dotenv_path=find_dotenv())
URL_PREFIX = os.environ.get("URL_PREFIX", None)
BASE_URL = os.environ.get("BASE_URL", None)

VERSION = "v0.0.1"
TITLE = "BIS Data Distribution API"
# This description is overrode by the DESCRIPTION def in v1/bis/__init.py
DESCRIPTION = ''

class BisApiRequest(Request):

    def __init__(self, environ, populate_request=True, shallow=False):
        super(BisApiRequest, self).__init__(environ, populate_request, shallow)
        """Request subclass to override base_url with BASE_URL env config param if present"""
        self.base_url = BASE_URL + self.path if BASE_URL else self.base_url

class BisApiFlask(Flask):
    """Flask subclass using the custom request class"""
    request_class = BisApiRequest

apidoc.url_prefix = URL_PREFIX or "/"
app = BisApiFlask(__name__)
CORS(app)

print("Serving Swagger from " + (URL_PREFIX or "/"))

'''
Custom Api to allow for relative serving of swagger.json
'''
class Custom_API(Api):
    @property
    def specs_url(self):
        '''
        The Swagger specifications absolute url (ie. `swagger.json`)

        :rtype: str
        '''
        return url_for(self.endpoint('specs'), _external=False)

blueprint = Blueprint("api", __name__, url_prefix=URL_PREFIX)
api = Custom_API(
    blueprint,
    default="BIS",
    default_label="About This Resource",
    title=TITLE,
    description='''
A read-only data distribution  api for USGS biogeographic information systems.
<div><a href='docs/api_info' target='_blank'><button class="btn">Additional Documentation</button></a></div>
''',
    version=VERSION,
)
app.register_blueprint(blueprint)


@api.route("/tir/api")
class BisApi(Resource):
    def get(self):
        return {"version": VERSION, "title": TITLE, "description": DESCRIPTION.replace("\n", " ").rstrip().lstrip()}

# Serve the Docusaurus docs at /docs
@app.route((URL_PREFIX or "") + "/docs/")
@app.route((URL_PREFIX or "") + "/docs/<path:path>")

def docs(path="index.html"):
    # If the path doesn't have an extension we need to point it to the appropriate file
    # This is necessary because Docusaurus uses client side routing and "clean" urls (no .html on the end)
    # In v1 of Docusaurus we could prevent this by setting `cleanUrl` to false in the config
    if len(path.split('.')) is 1:
        path += '/index.html'
    return send_from_directory('../docs', path)


from api.v1.bis.tir import *
