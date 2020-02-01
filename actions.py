import pandas as pd
import co2


def parse_uploaded_file(data):
    columns = ['from', 'to']

    df = pd.read_excel(data, columns=columns)

    df.columns = df.columns.str.lower()

    return df


def add_distances_to_df(df, distance_matrix, column_name='distances by car (km)'):
    # Returned object is organized by FROM, with each element in the reponse corresponding to TO
    # This means that for the simple DdB case we need to format as a column

    all_distances_in_km = [row['elements'][0]['distance']['value'] / 1000
                           for row in distance_matrix['rows']]

    assert len(all_distances_in_km) == len(df)
    df[column_name] = all_distances_in_km

    return df


def add_times_to_df(df, distance_matrix, column_name='time by car (hours'):
    all_times_in_hrs = [row['elements'][0]['duration']['value'] / 3600
                 for row in distance_matrix['rows']]
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

