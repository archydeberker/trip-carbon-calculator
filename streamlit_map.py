import streamlit as st
import pandas as pd

from mapping import google
from mapping.maps import plot_3d_map


@st.cache(allow_output_mutation=True)
def load_source_csv(path='/Users/archydeberker/Downloads/TD carbon distances time carbon calcv2.xls'):
    df = pd.read_excel(path)
    df.dropna(axis=0, how='any', inplace=True)
    return df


df = load_source_csv()
st.write(df)

df['from_lat'], df['from_lon'] = zip(*df['from'].apply(google.get_lat_lon_for_place))
df['to_lat'], df['to_lon'] = zip(*df['to'].apply(google.get_lat_lon_for_place))

map = plot_3d_map(df)
st.pydeck_chart(map)