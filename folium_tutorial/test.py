# Import Libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from folium.features import GeoJsonTooltip
import fiona
import json
import geojson as geoj

# Read the geoJSON file using geopandas
geojson = gpd.read_file('./georef-united-states-of-america-county.geojson')
# only select 'coty_code' (country fips) and 'geometry' columns
geojson = geojson[['coty_code', 'geometry']]

for index in geojson.index:
    geojson.loc[index, 'coty_code'] = ''.join(geojson.loc[index, 'coty_code'])

with open('./georef-united-states-of-america-county.geojson') as f:
    gj = geoj.load(f)
# features = "".join(gj['features'][0].properties['coty_code'])
# print(features)

for feature in gj['features']:
    feature.properties['coty_code'] = ''.join(feature.properties['coty_code'])

print(gj['features'][0])
