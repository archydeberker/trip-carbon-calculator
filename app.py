import os

import pandas as pd
from dotenv import load_dotenv

import actions
from flask import Flask, request, render_template, send_file, after_this_request, session
import tempfile
import traceback
import exceptions
import logging
from mapping import google, maps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(28)
GA_TRACKING_ID = os.environ.get("GA_TRACKING_ID")

logging.basicConfig(level=logging.INFO)


@app.route("/")
def upload_page():
    logging.info('Visitor to homepage')
    return render_template("file_upload.html", GA_TRACKING_ID=GA_TRACKING_ID)


@app.errorhandler(exceptions.InvalidFile)
def handle_invalid_usage(e):
    return render_template("file_upload.html", error=e.to_dict(), GA_TRACKING_ID=GA_TRACKING_ID)


@app.errorhandler(Exception)
def handle_unknown_error(e):
    app.logger.warning(traceback.format_exc())
    error = exceptions.UnknownError(str(e), e.args)
    return render_template("file_upload.html", error=error.to_dict(), GA_TRACKING_ID=GA_TRACKING_ID)


@app.route("/base")
def base():
    return render_template("base.html", GA_TRACKING_ID=GA_TRACKING_ID)


@app.route("/api/handle-upload", methods=["GET", "POST"])
def handle_upload():
    try:
        data = request.files["data"]

        original_df = actions.parse_uploaded_file(data)
        assert "count" in original_df

        df = google.add_trip_data_to_dataframe(original_df.copy())
        df = google.combine_with_original_dataframe(original_df, df)
        df = google.multiply_measures_by_count(df)

        assert len(df) == len(original_df)

    except Exception as e:
        raise e

    df = maps.add_coords_to_df(df)
    session["data"] = df.to_json(orient="records")
    total_co2 = df['total emissions (kg CO2)'].sum()
    logging.info(f'Uploaded file successfully handled, total CO2 {total_co2:.2f}')

    return render_template(
        "results.html",
        total_co2=f"{total_co2:.2f}",
        map=maps.clean_html(
            maps.plot_3d_map(df).to_html(as_string=True, iframe_width=800, iframe_height=800, notebook_display=False)
        ),
        GA_TRACKING_ID=GA_TRACKING_ID,
    )


@app.route("/api/download-results", methods=["GET"])
def download_results():
    data = session.get("data")
    df = pd.read_json(data, dtype=False)
    df = actions.format_data_for_download(df)
    temp = tempfile.NamedTemporaryFile(suffix=".xls")
    df.to_excel(temp.name, index=False)

    logging.info('File download successful')

    @after_this_request
    def teardown(response):
        temp.close()
        return response

    return send_file(temp.name, as_attachment=True, attachment_filename="processed.xls")


if __name__ == "__main__":
    app.run(debug=True)
