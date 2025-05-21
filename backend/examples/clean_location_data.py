import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import geopandas as gpd
import pandas as pd
from examples.examples_constants import RAW_DATA_PATH, PREPARED_DATA_PATH


def clean_location_data():
    admin_ribos_gdf = gpd.read_file(f'{RAW_DATA_PATH}/admin_ribos/admin_ribos.shp', encoding='utf-8')
    municipality_boundaries_gdf = admin_ribos_gdf[admin_ribos_gdf['ADMIN_LEVE'] == '5']
    district_boundaries_gdf = admin_ribos_gdf[admin_ribos_gdf['ADMIN_LEVE'] == '4']
    country_boundaries_gdf = admin_ribos_gdf[admin_ribos_gdf['ADMIN_LEVE'] == '2']
    elderly_municipality_boundaries_gdf1 = admin_ribos_gdf[admin_ribos_gdf['ADMIN_LEVE'] == '6']
    elderly_municipality_boundaries_gdf2 = admin_ribos_gdf[admin_ribos_gdf['ADMIN_LEVE'] == '10']
    new_rows = elderly_municipality_boundaries_gdf2[~elderly_municipality_boundaries_gdf2['NAME'].isin(elderly_municipality_boundaries_gdf1['NAME'])]
    elderly_municipality_boundaries_gdf = pd.concat([elderly_municipality_boundaries_gdf1, new_rows], ignore_index=True)
    elderly_municipality_boundaries_gdf = gpd.GeoDataFrame(elderly_municipality_boundaries_gdf, geometry='geometry')

    municipality_boundaries_gdf.to_file(f'{PREPARED_DATA_PATH}/municipality.geojson', driver='GeoJSON')
    district_boundaries_gdf.to_file(f'{PREPARED_DATA_PATH}/district.geojson', driver='GeoJSON')
    country_boundaries_gdf.to_file(f'{PREPARED_DATA_PATH}/country.geojson', driver='GeoJSON')
    elderly_municipality_boundaries_gdf.to_file(f'{PREPARED_DATA_PATH}/elderly_municipality.geojson', driver='GeoJSON')

