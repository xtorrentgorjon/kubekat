from flask import Flask, request, render_template
from flask import jsonify
#from flask_wtf import Form
#from wtforms import TextField
#from flask import jsonify
import random
import string

import json
import urllib.request

import argparse
import os


app = Flask(__name__)

INGRESS_TLS = os.environ['INGRESS_TLS']



VERSION = "0.1.0"

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


# Label-checker
@app.route("/label", methods = ['GET'])
def label_checker_call():
    response = urllib.request.urlopen('http://{}:80/api/v1/get/all'.format(os.environ['KUBEKAT_LABEL_CHECKER_SERVICE_HOST']))

    response_data = response.read()

    label_list = list(json.loads(response_data.decode("utf-8")))

    return jsonify(label_list)
    """
    response_data = response.read()

    pvc_list = list(json.loads(response_data.decode("utf-8")))

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return render_template('index_label_checker.html', url=request_url, version=VERSION, pvc_list=pvc_list)
    """

# Main
@app.route("/pvc", methods = ['GET'])
def pvc_checker_call():
    response = urllib.request.urlopen('http://{}:80/api/v1/get/all'.format(os.environ['KUBEKAT_PVC_CHECKER_SERVICE_HOST']))
    response_data = response.read()

    pvc_list = list(json.loads(response_data.decode("utf-8")))

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return render_template('index_pvc_checker.html', url=request_url, version=VERSION, pvc_list=pvc_list)



@app.route("/about.html", methods = ['GET'])
def aboutpage():
    return render_template('about.html')



if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
