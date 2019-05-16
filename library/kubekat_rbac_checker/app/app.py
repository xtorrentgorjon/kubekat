from flask import Flask, request, render_template
from flask import jsonify
from flask_wtf import Form
from wtforms import TextField
import random
import string

from rbac_checker.rbac_checker import rbac_checker
import argparse
import os

app = Flask(__name__)

INGRESS_TLS = True
#DEFAULT_FILTER = os.environ['DEFAULT_FILTER']
VERSION = "1.4.0"

app.config.update(dict(
    SECRET_KEY=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    WTF_CSRF_SECRET_KEY=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
))

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', help="Run in debug mode.", action='store_true')
args = parser.parse_args()

# This function prevents Flask from telling the browser to cache images indefinitely
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

class Filter_Form(Form):
   name = TextField("filter")


# First test
@app.route("/api/v1/get/all", methods = ['GET'])
def api_endpoint_all():
    filter = ['sla']
    form = Filter_Form()


    lc = rbac_checker(app)
    resources = lc.check_all_namespaces()
    app.logger.info('Detected rolebindings: {}'.format(resources))

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return jsonify(resources)


if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
