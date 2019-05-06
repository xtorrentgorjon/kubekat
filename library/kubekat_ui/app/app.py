from flask import Flask, request, render_template
from flask import jsonify
from flask_wtf import Form
from wtforms import TextField
#from flask import jsonify
import random
import string

import werkzeug

import json
import urllib.request

import argparse
import os


app = Flask(__name__)

INGRESS_TLS = os.environ['INGRESS_TLS']
VERSION = "0.3.0"

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', help="Run in debug mode.", action='store_true')
args = parser.parse_args()

app.config.update(dict(
    SECRET_KEY=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)),
    WTF_CSRF_SECRET_KEY=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
))

class Filter_Form(Form):
   filter = TextField("filter")

def string_to_list(input_string):
    filter_list = input_string.split(",")
    filter_list = [x.strip() for x in filter_list]
    return filter_list

def list_without_special_characters(input_list):
    return str(input_list).lstrip('[').rstrip(']').replace('"', '').replace("'","")



# This function prevents Flask from telling the browser to cache images indefinitely
@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

# Error handlers

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def error_http_500(e):
    error_title = "500 Error"
    error_text = "Internal Server Error"
    error_pic = "images/error-http-500.jpg"
    return render_template('error-http.html', version=VERSION, error_title=error_title, error_text=error_text, error_pic=error_pic), 500

@app.errorhandler(werkzeug.exceptions.NotFound)
def error_http_404(e):
    error_title = "404 Error"
    error_text = "Page Not Found"
    error_pic = "images/error-http-404.jpg"
    return render_template('error-http.html', version=VERSION, error_title=error_title, error_text=error_text, error_pic=error_pic), 404


@app.route("/error-http-500-test", methods = ['GET'])
def error500():
    raise Exception('Oops')
    return render_template('about.html')




# Label-checker
@app.route("/label", methods = ['GET', 'POST'])
def label_checker_call():
    filter_list_str = 'sla'
    form = Filter_Form()

    app.logger.info('Current filter is set to: <{}>'.format(form.filter.data))

    request_url = ""

    if form.filter.data:
        filter_list_str = form.filter.data

    filter_list = filter_list_str.split(",")

    request_url = 'http://{}:80/api/v1/get/filter?'.format(os.environ['KUBEKAT_LABEL_CHECKER_SERVICE_HOST'])
    request_url = request_url + filter_list[0].strip().replace(":", "=")
    if len(filter_list) > 1:
        for filter in filter_list[1:]:
            request_url = request_url + "&" + filter.strip().replace(":", "=")

    app.logger.info('Endpoint to be called is: < {} >'.format(request_url))

    #try:
    #    response = urllib.request.urlopen(request_url)
    #except e:
    #    app.logger.info('Error: < {} >'.format(e))
    response = urllib.request.urlopen(request_url)
    #response = urllib.request.urlopen('http://{}:80/api/v1/get/all'.format(os.environ['KUBEKAT_LABEL_CHECKER_SERVICE_HOST']))
    response_data = response.read()
    label_list = list(json.loads(response_data.decode("utf-8")))
    #return jsonify(label_list)

    correct_resources=label_list[0]["matched"]
    incorrect_resources=label_list[0]["unmatched"]

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return render_template('index_label_checker.html', url=request_url,
        version=VERSION, correct_resources=correct_resources, incorrect_resources=incorrect_resources,
        form=form, str_filter=filter_list_str)


# Main
@app.route("/pvc", methods = ['GET'])
def pvc_checker_call():
    response = urllib.request.urlopen('http://{}:80/api/v1/get/all'.format(os.environ['KUBEKAT_PVC_CHECKER_SERVICE_HOST']))
    response_data = response.read()

    pvc_list = list(json.loads(response_data.decode("utf-8")))
    app.logger.info('Received pvc list: %s', pvc_list)

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
