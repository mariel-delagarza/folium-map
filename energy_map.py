"""Modules to process data"""
import json
import requests
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip
import geojson as geoj
import choropleth_layer

# get csv from google sheet, turn into pandas dataframe
data = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vRUKtBM0I1eo7HVni3eWJOxNSidviWa7wN2JbTHO4tizb5ffIG0_f1BsYNp32eCXkKiSE9nW67WT_ud/pub?gid=1518327281&single=true&output=csv')
pd.DataFrame(data).to_csv('commodity_exports.csv', index=False)
commodity_exports_df = pd.DataFrame(data)

# Read the geojson file using geopandas, only select state_id and geometry
geojson = gpd.read_file('./states.geojson')
geojson = geojson[['state_id', 'geometry']]

# store geojson in variable to use in map
with open('./states.geojson') as f:
    gj = geoj.load(f)

# join CSV + geo data
df_final = geojson.merge(commodity_exports_df, left_on="state_id",
                         right_on="state_id", how="outer")

us_map = folium.Map(location=[40, -96],
                    zoom_start=4, tiles=None, overlay=False)
fg1 = folium.FeatureGroup(
    name='2020 Exports of Coal to Canada', overlay=False).add_to(us_map)
fg2 = folium.FeatureGroup(
    name='2020 Exports of RPP to Canada', overlay=False).add_to(us_map)
custom_scale1 = (df_final['coal'].quantile(
    (0, 0.25, 0.5, 0.75, 1))).tolist()
custom_scale2 = (df_final['rpp'].quantile(
    (0, 0.25, 0.5, 0.75, 1))).tolist()

coal = choropleth_layer.make_choropleth(gj, df_final, [
                                        'state_id', 'coal'], 'feature.properties.state_id', custom_scale1, 'Greys', 'White', '2020 Exports of Coal to Canada', fg1)

rpp = choropleth_layer.make_choropleth(gj, df_final, ['state_id', 'rpp'], 'feature.properties.state_id',
                                       custom_scale2, 'Blues', 'White', '2020 Exports of Raw Petroleum Products to Canada', fg2)

folium.features.GeoJson(
    data=df_final,
    name='2020 Exports of Coal to Canada',
    smooth_factor=2,
    style_function=lambda x: {'color': 'black',
                              'fillColor': 'transparent', 'weight': 0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['state', 'coal'
                ],
        aliases=["State:",
                 "Total USD:"
                 ],
        localize=True,
        sticky=False,
        labels=True,
        style="""
                            background-color: #F0EFEF;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """,
        max_width=800,),
    highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
).add_to(coal)

folium.features.GeoJson(
    data=df_final,
    name='2020 Exports of Raw Petroleum Products to Canada',
    smooth_factor=2,
    style_function=lambda x: {'color': 'black',
                              'fillColor': 'transparent', 'weight': 0.5},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['state', 'rpp'
                ],
        aliases=["State:",
                 "Total USD:"
                 ],
        localize=True,
        sticky=False,
        labels=True,
        style="""
                            background-color: #F0EFEF;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """,
        max_width=800,),
    highlight_function=lambda x: {'weight': 3, 'fillColor': 'grey'},
).add_to(rpp)

folium.TileLayer('cartodbpositron', overlay=True, name="").add_to(fg1)
folium.TileLayer('cartodbpositron', overlay=True, name="").add_to(fg2)

folium.LayerControl(collapsed=False).add_to(us_map)
us_map

us_map.save('index.html')
print('success')
