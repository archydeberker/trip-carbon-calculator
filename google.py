import googlemaps
import os
import pandas as pd

KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=KEY)


def get_distances(df):

    origins = df['from'].unique()
    destinations = df['to'].unique()

    # TODO: This will work if there is only one destination (as for DdB) but will be hugely
    # inefficient otherwise, so let's fix this

    # TODO add handling of multiple modes of transport
    distance_matrix = gmaps.distance_matrix(origins, destinations)

    return distance_matrix


def group_queries(df):
    """
    We want to make as few queries to the API as possible. The distance matrix does a cross-
    product of origins and destinations, so we're going to take in a dataframe and return
    subdataframe grouped by destination.

    TODO: factorize by origin too
    TODO: finish and think through!

    """
    df = df.groupby('to')
    return [df.get_group(x) for x in df.groups]


if __name__ == '__main__':
    df = pd.DataFrame()
    print(get_distances())

