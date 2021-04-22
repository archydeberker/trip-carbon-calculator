import logging
from multiprocessing import cpu_count, Pool
from typing import List
import numpy as np

import googlemaps
import os
import pandas as pd
import requests
import actions


KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=KEY)

logging.basicConfig(level=logging.INFO)

MAX_LOCATIONS = 25


def call_geocoding_api(place):
    req = f"https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={KEY}"
    response = requests.get(req)
    return response.json()


def get_lat_lon_for_place(place: str):
    response = call_geocoding_api(place)
    try:
        location = response["results"][0]["geometry"]["location"]
        lat, lon = location["lat"], location["lng"]
    except IndexError:
        logging.warning(f"Failed for {place}, returning nan")
        lat, lon = np.nan, np.nan

    return {place: (lat, lon)}


def combine_distance_matrix_results(results: List[dict]):
    """
    Combine a series of distance matrix results into one
    """
    out = results[0]
    for other_results in results[1:]:
        for key, value in other_results.items():
            out[key] += value
    return out


def get_distance_matrix_for_row(row):
    """
    Google supports a maximum size of 25 x 25, see
    https://stackoverflow.com/questions/52033446/max-dimensions-exceeded-distancematrix-error
    """
    return gmaps.distance_matrix(row["from"], row["to"])


def handle_one_row(row: pd.Series):
    distance_matrix = get_distance_matrix_for_row(row)

    # We now need to explode the factorized df to add back in the values
    exploded_df = pd.DataFrame(row).T.explode("from").explode("to")
    distance_list = unpack_distance_mtx_rows(distance_matrix)

    exploded_df = actions.add_distances_to_df(exploded_df, distance_list)
    exploded_df = actions.add_times_to_df(exploded_df, distance_list)
    exploded_df = actions.add_carbon_estimates_to_df(exploded_df)
    exploded_df = actions.add_flight_equivalent_to_df(exploded_df)

    return exploded_df


def add_trip_data_to_dataframe(df, factorize=True):

    # TODO add handling of multiple modes of transport
    # TODO turn off factorization
    factorized_df = group_queries(df)

    # Because the keys in the distance matrices that are returned don't exactly match
    # our initial queries, we have to handle the reconstitution in this function. We will
    # then combine our df's again

    inputs = []

    # First compile the inputs for multiprocessing; there might be a faster way to do this
    for _, row in factorized_df.iterrows():
        inputs.append(row)

    # Process each row in parallel
    p = Pool(cpu_count() - 1)
    out = p.map(handle_one_row, inputs)

    logging.info("All API calls complete")

    out_df = pd.concat(out)

    return out_df


def multiply_measures_by_count(
    df,
    distance_column_name="distance by car (km)",
    co2_column_name="emissions (kg CO2)",
    time_column_name="time by car (hours)",
    total_prefix="total",
):

    for col in [distance_column_name, time_column_name, co2_column_name]:
        df[" ".join((total_prefix, col))] = df[col] * df["count"]

    return df


def combine_with_original_dataframe(input, output):
    """The user may have included duplicates in their input. These will have been lost
    in the output as a result of the factorization process. We therefore need to join
    input to output"""
    return input.merge(output, on=["from", "to"], how="left")


def unpack_distance_mtx_rows(distance_matrix):
    # Returned object is organized by FROM, with each element in the response corresponding to TO
    # To convert it into the same format as the dataframe we have to unzip that
    out = []
    for _from in distance_matrix["rows"]:
        for _to in _from["elements"]:
            out.append(_to)

    return out


def filter_for_multiples(df, key="from"):
    multiple_records = df.apply(lambda x: len(x[key]) > 1, axis=1)

    return df.loc[multiple_records]


def factorize_locations(df):
    gb_from = df.groupby(["from"])["to"].unique().reset_index()
    gb_to = df.groupby(["to"])["from"].unique().reset_index()

    # Drop all non-grouped locations from gb_from
    gb_from = filter_for_multiples(gb_from, key="to")

    # Now figure out which ones we want from gb_to
    out = []
    for _, i in gb_to.iterrows():
        if len(i["from"]) == 1:
            _from = i["from"][0]
            if _from in gb_from["from"].values:
                # We already have it
                pass
            else:
                # Not part of the other groupby
                out.append(i)
        else:
            # It's a group, we definitely want it
            out.append(i)

    factorized_df = gb_from.append(out)

    return factorized_df


def group_queries(df, max_locations=MAX_LOCATIONS):
    """
    We want to make as few queries to the API as possible. The distance matrix does a cross-
    product of origins and destinations, so we're going to take in a dataframe and return
    subdataframe grouped by destination.

    TODO: factorize by origin too
    TODO: finish and think through!

    """

    # Each row of this is a single API call
    df = factorize_locations(df)

    # Some rows may be too large for the Google Maps API, so we should "unfactorize" those
    out = []
    for _, row in df.iterrows():
        n_from =  len(row['from'])
        for idx in range(0, n_from, max_locations):
            end = np.min((idx + max_locations, n_from))
            new_row = pd.DataFrame(data=np.asarray([(row["from"][idx:end], row["to"])]),
                                   columns=['from', 'to'])
            out.append(new_row)

    df_for_API_calls = pd.concat(out)

    return df_for_API_calls


if __name__ == "__main__":
    df = pd.DataFrame()
    print(add_trip_data_to_dataframe())
