import folium


def make_choropleth(geo_data, data, columns, key_on, threshold_scale, fill_color, nan_fill_color, legend_name, figure):

    layer = folium.Choropleth(
        geo_data=geo_data,
        data=data,
        # Here we tell folium to get the state_ids and plot new_cases_7days metric for each county
        columns=columns,
        # Here we grab the geometries/county boundaries from the geojson file using the key 'coty_code' which is the same as county fips
        key_on=key_on,
        threshold_scale=threshold_scale,  # use the custom scale we created for legend
        fill_color=fill_color,
        # Use white color if there is no data available for the county
        nan_fill_color=nan_fill_color,
        fill_opacity=0.7,
        line_opacity=0.2,
        # title of the legend
        legend_name=legend_name,
        highlight=True,
        line_color='black').geojson.add_to(figure)

    return layer
