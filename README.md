# 🚗 Trip CO2 Estimator

This small webapp and API allows you to upload
an Excel file with two columns - Origins and Destinations - 
and retrieve a modified Excel with the following information added:
- Time to drive between destinations
- Distance to drive between destinations
- CO2 emissions for the journey, using UK average emissions data
from the [gov.uk]( https://www.gov.uk/government/statistics/vehicle-licensing-statistics-2018)
- The number of transatlantic flights to which your trip is equivalent, in terms of CO2 emissions

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

# Logic
Typical data uploaded to this service involves many duplicate origins and destinations.

To avoid many redundant calls to the distance matrix API, we first 
factorize by destination. This allows us to make calls to the API
where we have a single destination and all of the relevant origins.

However, if there are more than 25 origins, we have a problem, because 
Google's Distance Matrix API won't allow us to submit a query with more than 25
locations in the rows or columns. If there are more than 25 origins for a single
destination, we split our calls and recombine them afterwards.