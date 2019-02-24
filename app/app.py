from flask import Flask, request, render_template
from flask_wtf import Form
from wtforms import TextField
import random
import string

from functions.functions import *
import argparse
import os

app = Flask(__name__)

INGRESS_TLS = os.environ['INGRESS_TLS']
DEFAULT_FILTER = os.environ['DEFAULT_FILTER']
VERSION = "1.3.0"

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

def string_to_list(input_string):
    filter_list = input_string.split(",")
    filter_list = [x.strip() for x in filter_list]
    return filter_list

def list_without_special_characters(input_list):
    return str(input_list).lstrip('[').rstrip(']').replace('"', '').replace("'","")

# Main
@app.route("/", methods = ['GET', 'POST'])
def application_bootstrap():
    filter = [DEFAULT_FILTER]
    form = Filter_Form()

    if form.validate_on_submit():
        filter = form.name.data
        filter = string_to_list(filter)


    lc = label_checker(app)
    resources = lc.check_all_namespaces()
    app.logger.info('Detected apps: %s', resources)
    lc.filter_resource_by_label(filter)
    correct_resources, incorrect_resources = lc.get_correct_resources(), lc.get_incorrect_resources()

    request_url = "http://"+request.host
    if (INGRESS_TLS == "True"):
        request_url = "https://"+request.host

    str_filter=list_without_special_characters(filter)

    return render_template('bootstrap.html',
        form = form, correct_resources=correct_resources,
        incorrect_resources=incorrect_resources,
        str_filter=str_filter, url=request_url, version=VERSION)


@app.route("/about.html", methods = ['GET'])
def aboutpage():
    return render_template('about.html')



if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
