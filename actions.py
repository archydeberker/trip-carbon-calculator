from typing import List

import pandas as pd
import co2
import exceptions
import numpy as np

from flask import session

import logging

logger = logging.getLogger(__name__)


def store_output_in_session(data):
    logger.info("Placing data into session")
    session["data"] = data


def retrieve_output_from_session():
    logger.info("Retrieving data from session")
    return session.get("data")


def parse_uploaded_file(data):
    try:
        df = pd.read_excel(data)
        df.columns = df.columns.str.lower()
    except Exception as e:
        logging.critical(e)
        raise exceptions.InvalidFile(str(e))

    df = df.filter(items=["from", "to", "count"], axis=1)

    if not np.array_equal(df.columns, ["from", "to"]) and not np.array_equal(df.columns, ["from", "to", "count"]):
        logging.critical("Invalid file error")
        raise exceptions.InvalidFile(
            """
            Please make sure your excel includes the columns 'from' and 'to', with optional 'count'!
            """
        )

    # If there was no count column, add one
    if "count" not in df:
        df["count"] = 1

    return df


def validate_distance_matrix_results(distance_list: List, df: pd.DataFrame):
    for i, item in enumerate(distance_list):
        try:
            assert "distance" in item
        except AssertionError:
            logging.warning(f"Problem getting a distance for row {df.iloc[i]}")
            logging.warning(item)
            logging.warning(df.iloc[i])

            distance_list[i] = {"distance": {"value": np.nan}, "duration": {"value": np.nan}}


def add_distances_to_df(df, distance_list, column_name="distance by car (km)"):

    validate_distance_matrix_results(distance_list, df)

    all_distances_in_km = [item["distance"]["value"] / 1000 for item in distance_list]

    assert len(all_distances_in_km) == len(df)
    df[column_name] = all_distances_in_km

    return df


def add_times_to_df(df, distance_list, column_name="time by car (hours)"):
    all_times_in_hrs = [item["duration"]["value"] / 3600 for item in distance_list]

    assert len(all_times_in_hrs) == len(df)
    df[column_name] = all_times_in_hrs

    return df


def add_carbon_estimates_to_df(
    df, distance_column_name="distance by car (km)", emissions_column_name="emissions (kg CO2)"
):
    """
    df needs to already have the distance column in.

    By default this calculation happens in kg.
    """

    df[emissions_column_name] = df[distance_column_name].apply(co2.calculate_co2)
    return df


def add_flight_equivalent_to_df(
    df, emissions_column_name="emissions (kg CO2)", flight_column_name="transatlantic flight equivalents (flights)"
):
    df[flight_column_name] = df[emissions_column_name].apply(co2.calculate_flight_equivalent)
    return df


def format_data_for_download(df):
    df.drop(["from_lon", "to_lon", "from_lat", "to_lat"], axis=1, inplace=True)
    return df
