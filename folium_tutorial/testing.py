# Import Libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from folium.features import GeoJsonTooltip
import geojson as geoj

with open('./georef-united-states-of-america-county.geojson') as f:
    gj = geoj.load(f)

for feature in gj['features']:
    feature.properties['coty_code'] = ''.join(feature.properties['coty_code'])


# Read the geoJSON file using geopandas
geojson = gpd.read_file('./georef-united-states-of-america-county.geojson')
# only select 'coty_code' (country fips) and 'geometry' columns
geojson = geojson[['coty_code', 'geometry']]

print(geojson.head())

for index in geojson.index:
    geojson.loc[index, 'coty_code'] = ''.join(geojson.loc[index, 'coty_code'])


# Read the covid-19 data using pandas
covid_df = pd.read_csv('./United_States_COVID-19.csv')


# change the data type of 'fips_code' to string and fill the leading zero
covid_df["fips_code"] = covid_df["fips_code"].map(str)
covid_df["fips_code"] = covid_df["fips_code"].str.zfill(5)

# Filter the dataframe to only show records for 2021/12/29
covid_df = covid_df[(covid_df['report_date'] == '2021/12/29')]

# create two new columns with correct data types and formats and drop the original columns.
covid_df['new_cases_7days'] = covid_df['cases_per_100K_7_day_count_change'].str.replace(
    ',', '')
covid_df['new_cases_7days'] = covid_df['new_cases_7days'].replace(
    {'suppressed': np.nan}).astype(float)
covid_df['pct_positive_7days'] = covid_df['percent_test_results_reported_positive_last_7_days']/100
covid_df.drop(['cases_per_100K_7_day_count_change', 'percent_test_results_reported_positive_last_7_days',
              'community_transmission_level'], axis=1, inplace=True)

# Join the geojson file with covid_df
df_final = geojson.merge(covid_df, left_on="coty_code",
                         right_on="fips_code", how="outer")
df_final = df_final[~df_final['geometry'].isna()]


us_map = folium.Map(location=[40, -96], zoom_start=4, tiles='openstreetmap')

# Create the choropleth map add it to the base map
custom_scale = (df_final['new_cases_7days'].quantile(
    (0, 0.2, 0.4, 0.6, 0.8, 1))).tolist()
folium.Choropleth(
    geo_data=gj,
    data=df_final,
    # Here we tell folium to get the county fips and plot new_cases_7days metric for each county
    columns=['fips_code', 'new_cases_7days'],
    # Here we grab the geometries/county boundaries from the geojson file using the key 'coty_code' which is the same as county fips
    key_on='feature.properties.coty_code',
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
