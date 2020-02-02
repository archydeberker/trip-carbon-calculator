import pandas as pd
import co2
import exceptions
import numpy as np


def parse_uploaded_file(data):
    columns = ['from', 'to']
    try:
        df = pd.read_excel(data, columns=columns)
        df.columns = df.columns.str.lower()
    except Exception as e:
        print(e)
        raise exceptions.InvalidFile(str(e))

    if not np.array_equal(df.columns, ['from', 'to']):
        raise exceptions.InvalidFile('''
            Please make sure your excel format has two columns 'from' and 'to'!
            ''')
    return df


def add_distances_to_df(df, distance_list, column_name='distances by car (km)'):

    all_distances_in_km = [item['distance']['value'] / 1000
                           for item in distance_list]

    assert len(all_distances_in_km) == len(df)
    df[column_name] = all_distances_in_km

    return df


def add_times_to_df(df, distance_list, column_name='time by car (hours)'):
    all_times_in_hrs = [item['duration']['value'] / 3600
                           for item in distance_list]

    assert len(all_times_in_hrs) == len(df)
    df[column_name] = all_times_in_hrs

    return df


def add_carbon_estimates_to_df(df, distance_column_name='distances by car (km)',
                               emissions_column_name='emissions (kg CO2)'):
    """
    df needs to already have the distance column in.

    By default this calculation happens in kg.
    """

    df[emissions_column_name] = df[distance_column_name].apply(co2.calculate_co2)
    return df


def add_flight_equivalent_to_df(df, emissions_column_name='emissions (kg CO2)',
                                flight_column_name='transatlantic flight equivalents (flights)'):
    df[flight_column_name] = df[emissions_column_name].apply(co2.calculate_flight_equivalent)
    return df
