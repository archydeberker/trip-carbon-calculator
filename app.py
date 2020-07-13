import os

import pandas as pd

import actions
from flask import Flask, request, render_template, send_file, after_this_request, session
import tempfile
import traceback
import exceptions
from mapping import google, maps

app = Flask(__name__)
app.secret_key = os.urandom(28)


@app.route('/')
def upload_page():
    return render_template('file_upload.html')


@app.errorhandler(exceptions.InvalidFile)
def handle_invalid_usage(e):
    return render_template('file_upload.html', error=e.to_dict())


@app.errorhandler(Exception)
def handle_unknown_error(e):
    app.logger.warning(traceback.format_exc())
    error = exceptions.UnknownError(str(e), e.args)
    return render_template('file_upload.html', error=error.to_dict())


@app.route('/api/handle-upload', methods=['GET', 'POST'])
def handle_upload():
    try:
        data = request.files['data']

        original_df = actions.parse_uploaded_file(data)

        df = google.add_trip_data_to_dataframe(original_df.copy())

        output_df = google.combine_with_original_dataframe(original_df, df)

        assert len(output_df) == len(original_df)

    except Exception as e:
        raise e

    df = maps.add_coords_to_df(df)
    session["data"] = df.to_json(orient='records')

    return render_template('results.html', map=maps.clean_html(maps.plot_3d_map(df).to_html(as_string=True,
                                                                            iframe_width=800,
                                                                            iframe_height=800,
                                                                            notebook_display=False
                                                                            )))


@app.route('/api/download-results', methods=['GET'])
def download_results():
    data = session.get('data')
    df = pd.read_json(data, dtype=False)
    temp = tempfile.NamedTemporaryFile(suffix='.xls')
    df.to_excel(temp.name, index=False)

    @after_this_request
    def teardown(response):
        temp.close()
        return response

    return send_file(temp.name, as_attachment=True, attachment_filename='processed.xls')


if __name__ == "__main__":
    app.run(debug=True)