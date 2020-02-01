import os
import actions
from flask import Flask, request, render_template, url_for, redirect, send_file, after_this_request
import tempfile

import google

app = Flask(__name__)


@app.route('/')
def upload_page():
    return render_template('file_upload.html')


@app.route('/api/handle-upload', methods=['GET', 'POST'])
def handle_upload():
    if 'data' in request.files:
        data = request.files['data']

        df = actions.parse_uploaded_file(data)

        distance_matrix = google.get_distances(df)

        df = actions.add_distances_to_df(df, distance_matrix)
        df = actions.add_times_to_df(df, distance_matrix)
        df = actions.add_carbon_estimates_to_df(df)

        temp = tempfile.NamedTemporaryFile(suffix='.xls')

        df.to_excel(temp.name)

        # @after_this_request
        # def teardown(response):
        #     temp.close()

        return send_file(temp.name, as_attachment=True, attachment_filename='processed.xls')
    else:
        return "File not found"


if __name__ == "__main__":
    app.run(debug=True)