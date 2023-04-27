"""Modules to process data"""
import json
import requests
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip
import geojson as geoj

# fetch google sheet
res = requests.get('https://sheets.googleapis.com/v4/spreadsheets/19uN6jYmrvuXwwrcOnwpTlQSJAEYP9gH6TQdq3Jn4z94/values/Commodity_Exports!A1:J?key=AIzaSyAImbihK2tiRewSFzuJTF_lcgPlGSr7zcg')
# turn google sheet into json
response = json.loads(res.text)

# get json values, turn into CSV
arr = np.asarray(response['values'])
pd.DataFrame(arr).to_csv('commodity_exports.csv', index=False, header=False)
commodity_exports_df = pd.read_csv('./commodity_exports.csv')

print(commodity_exports_df.info())

# Read the geojson file using geopandas
geojson = gpd.read_file('./states.geojson')
# only select state_id and geometry
geojson = geojson[['state_id', 'geometry']]
print(geojson.head())

with open('./states.geojson') as f:
    gj = geoj.load(f)

df_final = geojson.merge(commodity_exports_df, left_on="state_id",
                         right_on="state_id", how="outer")
df_final = df_final[~df_final['geometry'].isna()]

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

coal = folium.Choropleth(
    geo_data=gj,
    data=df_final,
    # Here we tell folium to get the state_ids and plot new_cases_7days metric for each county
    columns=['state_id', 'coal'],
    # Here we grab the geometries/county boundaries from the geojson file using the key 'coty_code' which is the same as county fips
    key_on='feature.properties.state_id',
    threshold_scale=custom_scale1,  # use the custom scale we created for legend
    fill_color='Greys',
    nan_fill_color="White",  # Use white color if there is no data available for the county
    fill_opacity=0.7,
    line_opacity=0.2,
    # title of the legend
    legend_name='2020 Exports of Coal to Canada',
    highlight=True,
    line_color='black').geojson.add_to(fg1)

rpp = folium.Choropleth(
    geo_data=gj,
    data=df_final,
    # Here we tell folium to get the state_ids and plot new_cases_7days metric for each county
    columns=['state_id', 'rpp'],
    # Here we grab the geometries/county boundaries from the geojson file using the key 'coty_code' which is the same as county fips
    key_on='feature.properties.state_id',
    threshold_scale=custom_scale2,  # use the custom scale we created for legend
    fill_color='Blues',
    nan_fill_color="White",  # Use white color if there is no data available for the county
    fill_opacity=0.7,
    line_opacity=0.2,
    # title of the legend
    legend_name='2020 Exports of Raw Petroleum Products to Canada',
    highlight=True,
    line_color='black').geojson.add_to(fg2)
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
