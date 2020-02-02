import os

import xlrd

import actions
from flask import Flask, request, render_template, url_for, redirect, send_file, after_this_request
import tempfile

import exceptions
import google

app = Flask(__name__)


@app.route('/')
def upload_page():
    return render_template('file_upload.html')


@app.route('/api/handle-upload', methods=['GET', 'POST'])
def handle_upload():
    if 'data' in request.files:
        try:
            data = request.files['data']

            df = actions.parse_uploaded_file(data)

            distance_matrix = google.get_distances(df)

            df = actions.add_distances_to_df(df, distance_matrix)
            df = actions.add_times_to_df(df, distance_matrix)
            df = actions.add_carbon_estimates_to_df(df)

            temp = tempfile.NamedTemporaryFile(suffix='.xls')

            df.to_excel(temp.name)

        except (xlrd.biffh.XLRDError, TypeError) as e:

            error = exceptions.InvalidFile(str(e), e.args)
            return render_template('file_upload.html', error=error.to_dict())

        except Exception as e:
            error = exceptions.UnknownError(str(e), e.args)
            return render_template('file_upload.html', error=error.to_dict())

        @after_this_request
        def teardown(response):
            temp.close()
            return response

        return send_file(temp.name, as_attachment=True, attachment_filename='processed.xls')
    else:
        return render_template('file_upload.html', error="Please upload a valid Excel file")


if __name__ == "__main__":
    app.run(debug=True)