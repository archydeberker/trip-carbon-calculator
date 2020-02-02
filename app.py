import os

import xlrd
from werkzeug.exceptions import InternalServerError

import actions
from flask import Flask, request, render_template, url_for, redirect, send_file, after_this_request, \
    jsonify
import tempfile

import exceptions
import google

app = Flask(__name__)


@app.route('/')
def upload_page():
    return render_template('file_upload.html')


@app.errorhandler(exceptions.InvalidFile)
def handle_invalid_usage(e):
    return render_template('file_upload.html', error=e.to_dict())


@app.errorhandler(Exception)
def handle_unknown_error(e):
    error = exceptions.UnknownError(str(e), e.args)
    return render_template('file_upload.html', error=error.to_dict())


@app.route('/api/handle-upload', methods=['GET', 'POST'])
def handle_upload():
    try:
        data = request.files['data']

        df = actions.parse_uploaded_file(data)

        distance_matrix = google.get_distances(df)

        df = actions.add_distances_to_df(df, distance_matrix)
        df = actions.add_times_to_df(df, distance_matrix)
        df = actions.add_carbon_estimates_to_df(df)

        temp = tempfile.NamedTemporaryFile(suffix='.xls')

        df.to_excel(temp.name)

    except Exception as e:
        raise e

    @after_this_request
    def teardown(response):
        temp.close()
        return response

    return send_file(temp.name, as_attachment=True, attachment_filename='processed.xls')



if __name__ == "__main__":
    app.run(debug=True)