from flask import Flask, request, render_template
from flask import jsonify
from flask_wtf import Form
from wtforms import TextField
import random
import string

from label_checker.label_checker import label_checker
import argparse
import os

app = Flask(__name__)

INGRESS_TLS = os.environ['INGRESS_TLS']
DEFAULT_FILTER = os.environ['DEFAULT_FILTER']
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

def string_to_list(input_string):
    filter_list = input_string.split(",")
    filter_list = [x.strip() for x in filter_list]
    return filter_list

def list_without_special_characters(input_list):
    return str(input_list).lstrip('[').rstrip(']').replace('"', '').replace("'","")


@app.route("/api/v1/get/filter", methods = ['GET'])
def api_endpoint_filter():
    filter_list = []

    for http_arg in request.args:
        app.logger.debug('Received filter: < {} {} {} >'.format(http_arg, request.args.get(http_arg), type(request.args.get(http_arg))))
        filter = http_arg
        filter_value = request.args.get(http_arg)

        if filter_value != "":
            filter = filter + ":" + filter_value
        filter_list.append(filter)

    app.logger.debug('Received filter: < {} >'.format(filter_list))

    lc = label_checker(app)
    resources = lc.check_all_namespaces()
    #app.logger.info('Detected apps: {}'.format(resources))
    lc.filter_resource_by_label(filter_list)
    matched_resources, unmatched_resources = lc.get_correct_resources(), lc.get_incorrect_resources()

    app.logger.debug('Returning response lengths: < Match: {} Unmatch: {} >'.format(len(matched_resources), len(unmatched_resources)))

    return jsonify([{"matched":matched_resources, "unmatched":unmatched_resources}])


# First test
@app.route("/api/v1/get/all", methods = ['GET'])
def api_endpoint_all():
    filter = ['sla']
    form = Filter_Form()


    lc = label_checker(app)
    resources = lc.check_all_namespaces()
    app.logger.info('Detected apps: {}'.format(resources))
    lc.filter_resource_by_label(filter)
    matched_resources, unmatched_resources = lc.get_correct_resources(), lc.get_incorrect_resources()

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    str_filter=list_without_special_characters(filter)

    return jsonify([{"matched":matched_resources, "unmatched":unmatched_resources}])


if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
