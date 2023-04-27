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

geojson = gpd.read_file('./states.geojson')

with open('./states.geojson') as f:
    gj = geoj.load(f)

df_final = geojson.merge(commodity_exports_df, left_on="state_id",
                         right_on="id", how="outer")
df_final = df_final[~df_final['geometry'].isna()]

us_map = folium.Map(location=[40, -96], zoom_start=4, tiles='openstreetmap')

custom_scale = (df_final['coal'].quantile(
    (0, 0.2, 0.4, 0.6, 0.8, 1))).tolist()

folium.Choropleth(
    geo_data=gj,
    data=df_final,
    # Here we tell folium to get the county fips and plot new_cases_7days metric for each county
    columns=['id', 'coal'],
    # Here we grab the geometries/county boundaries from the geojson file using the key 'coty_code' which is the same as county fips
    key_on='feature.properties.name',
    threshold_scale=custom_scale,  # use the custom scale we created for legend
    fill_color='YlOrRd',
    nan_fill_color="White",  # Use white color if there is no data available for the county
    fill_opacity=0.7,
    line_opacity=0.2,
    # title of the legend
    legend_name='New Cases Past 7 Days (Per 100K Population) ',
    highlight=True,
    line_color='black').add_to(us_map)

us_map

us_map.save('index.html')
