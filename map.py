import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

from mapping import google
LONDON = [51.50, -0.12]


@st.cache(allow_output_mutation=True)
def load_source_csv(path='/Users/archydeberker/Downloads/TD carbon distances time carbon calcv2.xls'):
    df = pd.read_excel(path)
    df.dropna(axis=0, how='any', inplace=True)
    return df


def plot_3d_map(df):
    """
    Plots a map with a dot at latitude `x` with longitude `y` and height `z`
    """
    df = df.copy()
    df['consults'] = df['number of consultations']
    cmap = plt.get_cmap('plasma')
    st.write(cmap(0))
    st.write(cmap(100))
    geojson = pdk.Layer(
        'ArcLayer',
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["to_lon", "to_lat"],
        get_source_color='[consults, 0, 255-consults , 128]',
        get_target_color='[consults, 0, 255-consults, 128]',
        stroke_width=100,
        data=df,
        opacity=0.6,
        get_normal=[0, 0, 15],
        auto_highlight=True,
        point_size=10,
        pickable=False
    )
    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=LONDON[1],
        latitude=LONDON[0],
        zoom=3,
        min_zoom=5,
        max_zoom=15,
        pitch=89,
        bearing=0)

    return st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                                    initial_view_state=view_state,
                           layers=[geojson]))


df = load_source_csv()
st.write(df)

df['from_lat'], df['from_lon'] = zip(*df['from'].apply(google.get_lat_lon_for_place))
df['to_lat'], df['to_lon'] = zip(*df['to'].apply(google.get_lat_lon_for_place))

plot_3d_map(df)