from flask import Flask, request, render_template
from flask_wtf import Form
from wtforms import TextField

from functions.functions import *
import argparse

app = Flask(__name__)

INGRESS_TLS = True

app.config.update(dict(
    SECRET_KEY="SECRETKEY_LMAO_ROFL",
    WTF_CSRF_SECRET_KEY="SECRETKEY_LMAO_ROFL"
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

# Main
@app.route("/", methods = ['GET', 'POST'])
def application():
    filter = ["sla"]
    form = Filter_Form()

    if form.validate_on_submit():
        filter = form.name.data
        filter = string_to_list(filter)

    app.logger.debug('Current filter %s', filter)
    app.logger.debug('Current filter type %s', type(filter))

    lc = label_checker(app)
    deployments = lc.check_all_namespaces()
    app.logger.info('Detected apps: %s', deployments)
    lc.filter_deployment_by_label(filter)
    correct_deployments = lc.get_correct_deployments()
    incorrect_deployments = lc.get_incorrect_deployments()

    request_url = "http://"+request.host
    if (INGRESS_TLS):
        request_url = "https://"+request.host

    return render_template('index.html',
        form = form, correct_deployments=correct_deployments,
        incorrect_deployments=incorrect_deployments, filter=filter,
        url=request_url)

@app.route("/about.html", methods = ['GET'])
def aboutpage():
    return render_template('about.html')



if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
