from flask import Flask, request, render_template

from functions.functions import *
import argparse

app = Flask(__name__)

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
@app.route("/")
def application():
    lc = label_checker(app)
    deployments = lc.check_all_namespaces()
    lc.filter_deployment_by_label(["sla"])
    app.logger.info('Detected apps: %s', deployments)
    correct_deployments = lc.get_correct_deployments()
    incorrect_deployments = lc.get_incorrect_deployments()

    return render_template('index.html', correct_deployments=correct_deployments, incorrect_deployments=incorrect_deployments)


if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
