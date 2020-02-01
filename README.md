# Trip CO2 Estimator

This small webapp and API allows you to upload
an Excel file with two columns - Origins and Destinations - 
and retrieve a modified Excel with the following information added:
- Time to drive between destinations
- Distance to drive between destinations
- CO2 emissions for the journey, using UK average emissions data
from the [gov.uk]( https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2018)

All route planning is done via the Google Maps [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/start).

## Requirements

- Python 3.7
- A Google Cloud account to provide you with an API key, which should
be exported as

```bash
export GOOGLE_MAPS_API_KEY=xxxx
```

## Running

- Create a virtual environment with the tool of your choice

Then 

```bash
pip install -r requirements.txt
```

You can then run the tests:

```bash
python -m pytest .
```

And assuming everything is passing, run the app:

```bash
python app.py
```

You should then be able to go to http://127.0.0.1:5000 to use the frontend,
or upload documents via POST request to http://127.0.0.1:5000/api/handle-upload.

