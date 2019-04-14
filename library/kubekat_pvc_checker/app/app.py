from flask import Flask, request, render_template
#from flask_wtf import Form
#from wtforms import TextField
from flask import jsonify
import random
import string

from pvc_checker.pvc_checker import pvc_checker
import argparse
import os

app = Flask(__name__)

INGRESS_TLS = os.environ['INGRESS_TLS']
VERSION = "0.1.2"

CACHE_RESULTS = []

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', help="Run in debug mode.", action='store_true')
args = parser.parse_args()


# This function prevents Flask from telling the browser to cache images indefinitely
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

# Main
@app.route("/api/v1/get/all", methods = ['GET'])
def api_endpoint_all():
    lc = pvc_checker(app)
    app.logger.error('New API request.')

    app.logger.error('Answering with kubekat pvc checker version {}'.format(VERSION))
    result = lc.check_all_namespaces()

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return jsonify(result)


if __name__ == "__main__":
    if(args.debug):
        app.logger.debug('Starting kubekat pvc checker version {}'.format(VERSION))
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
