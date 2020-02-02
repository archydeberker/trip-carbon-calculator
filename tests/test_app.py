import pandas as pd
import numpy as np
import pytest

import actions
import co2
import google


df = pd.DataFrame(data=[['Bristol, UK', 'Bath, UK'], ['London, UK', 'London, UK']],
                  index=['from', 'to']).T


@pytest.fixture(scope='module')
def distance_matrix():
    yield google.get_distances(df)


def test_loading_data_with_header():

    with open('tests/test_data/data_with_header.xlsx', 'rb') as f:
        data = f.read()

    df = actions.parse_uploaded_file(data)

    assert len(df) == 2
    assert np.array_equal(df.columns, ['from', 'to'])


def test_loading_data_without_header():
    #TODO: test the handling of situations where people forget the header!
    pass


def test_processing_of_df_to_call_google_maps(distance_matrix):
    np.testing.assert_array_equal(distance_matrix['destination_addresses'], df['to'].unique())
    np.testing.assert_array_equal(distance_matrix['origin_addresses'], df['from'].unique())


def test_directions_api_returns_results_equivalent_to_maps(distance_matrix):
    assert int(distance_matrix['rows'][0]['elements'][0]['distance']['value']/1000) == 189
    assert int(distance_matrix['rows'][1]['elements'][0]['distance']['value']/1000) == 184


def test_addition_of_distance_to_dataframe(distance_matrix):
    distance_list = google.unpack_distance_mtx_rows(distance_matrix)
    new_df = actions.add_distances_to_df(df.copy(), distance_list, column_name='dist')
    assert int(new_df['dist'].iloc[0]) == 189
    assert int(new_df['dist'].iloc[1]) == 184


def test_addition_of_co2_to_dataframe(distance_matrix):
    distance_list = google.unpack_distance_mtx_rows(distance_matrix)
    new_df = actions.add_distances_to_df(df.copy(), distance_list, column_name='dist')
    new_df = actions.add_carbon_estimates_to_df(new_df, distance_column_name='dist',
                                                emissions_column_name='emissions',
                                                )
    assert np.isclose(new_df['emissions'].iloc[0], co2.calculate_co2(189), atol=.5)
    assert np.isclose(new_df['emissions'].iloc[1], co2.calculate_co2(184), atol=.5)


def test_grouping_of_queries_does_not_affect_df(distance_matrix):
    grouped_df = google.group_queries(df)
    pd.testing.assert_frame_equal(grouped_df.explode('from').explode('to').reset_index(drop=True), df)


def test_grouping_of_queries_does_not_affect_results():
    dist