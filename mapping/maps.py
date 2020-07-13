import pydeck as pdk
from matplotlib import pyplot as plt

LONDON = [51.50, -0.12]


def add_coords_to_df(df):
    from mapping import google
    df['from_lat'], df['from_lon'] = zip(*df['from'].apply(google.get_lat_lon_for_place))
    df['to_lat'], df['to_lon'] = zip(*df['to'].apply(google.get_lat_lon_for_place))

    return df


def plot_3d_map(df):
    """
    Plots a map with a dot at latitude `x` with longitude `y` and height `z`
    """
    df = df.copy()
    df['count'] = df.get('count') or 1
    df['distance'] = df['distances by car (km)'].apply(lambda x: f"{x:.2f}")
    df['total_emissions'] = df['emissions (kg CO2)'].apply(lambda x: f"{x:.2f}")

    geojson = pdk.Layer(
        'ArcLayer',
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["to_lon", "to_lat"],
        get_source_color='[count, 0, 255-count , 255]',
        get_target_color='[count, 0, 255-count, 255]',
        stroke_width=1000,
        data=df,
        opacity=0.6,
        get_normal=[0, 0, 15],
        auto_highlight=True,
        point_size=10,
        pickable=True,
        tooltip=True,
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

    return pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=view_state,
                    layers=[geojson],
                    tooltip={
                        "html": "<b>Distance:</b> {distance} km<br/>"
                                "<b>Number of Trips:</b> {count} <br/>"
                                "<b>CO2 saved:</b> {total_emissions} kg <br/>"
                                "",
                        "style": {
                            "backgroundColor": "steelblue",
                            "color": "white"
                        }
                    },
                    width='70%',
                    height=200
                    )


def clean_html(html):
    html = html.replace('100vw', '100%').replace('100vw', '100%')
    return html