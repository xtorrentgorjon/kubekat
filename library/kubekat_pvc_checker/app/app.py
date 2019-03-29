from flask import Flask, request, render_template
#from flask_wtf import Form
#from wtforms import TextField
import random
import string

from pvc_checker.pvc_checker import pvc_checker
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


# Main
@app.route("/", methods = ['GET'])
def application():
    lc = pvc_checker(app)
    app.logger.info('New HTTP request.')
    global CACHE_RESULTS
    if CACHE_RESULTS == []:
        CACHE_RESULTS = lc.check_all_namespaces()

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return render_template('index.html', url=request_url, version=VERSION, pvc_list=CACHE_RESULTS)


@app.route("/about.html", methods = ['GET'])
def aboutpage():
    return render_template('about.html')



if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
