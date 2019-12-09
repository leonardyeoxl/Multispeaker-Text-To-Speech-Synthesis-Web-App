'''
print(sys.version)
api_1  | 3.6.9 |Anaconda, Inc.| (default, Jul 30 2019, 19:07:31) 
api_1  | [GCC 7.3.0]
'''
# standard library
from pathlib import Path

# external library
from flask import Flask, render_template
from waitress import serve

# project library
from blueprints.api import api
from blueprints.frontend import frontend

# global
app = Flask(__name__, static_folder='static', static_url_path='/static')
MAX_REQUEST_BODY_SIZE = 1024 * 1024 * 50 # can be uploaded upto 50 MB per request

app.register_blueprint(api)
app.register_blueprint(frontend)

if __name__ == "__main__":
    serve(app, listen='0.0.0.0:8080', max_request_body_size=MAX_REQUEST_BODY_SIZE)