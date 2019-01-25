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
    apps_with_missing_labels = lc.check_all_namespaces()
    app.logger.info('Detected apps: %s', apps_with_missing_labels)

    return render_template('index.html', var1="sjaakhazelollie", namespacelist=apps_with_missing_labels)


if __name__ == "__main__":
    if(args.debug):
        app.run(debug=True, host="0.0.0.0")
    else:
        app.run(host="0.0.0.0")
