

import geopandas as gpd
import pandas as pd

from constants import CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD, CONFIG_ADDITIONAL_DATA_GRID_LOCATION_COLUMN_FIELD, CONFIG_ADDITIONAL_DATA_LOCATION_COLUMN_FIELD, CONFIG_ADDITIONAL_DATA_NORMALIZE_FIELD, CONFIG_ADDITIONAL_DATA_PROPS, CONFIG_ADDITIONAL_DATA_VALUE_COLUMN_FIELD, CONFIG_BOUNDARIES_COLUMN_FIELD, CONFIG_BOUNDARIES_FILE_NAME_FIELD, CONFIG_BOUNDARIES_PROPS, CONFIG_GRID_ALREADY_NORMALIZED_COLUMNS, CONFIG_GRID_EXISTING_COLUMNS, CONFIG_GRID_FILE_NAME, CONFIG_GRID_ID_COLUMN, CONFIG_GRID_POPULATION_COLUMN, CONFIG_SURVEY_FILE_NAME, PROCESSED_GRID_FILE_NAME

def assign_grid_boundaries(grid_gdf, config, input_path):
    for boundaries_file_props in config[CONFIG_BOUNDARIES_PROPS]:
        boundary_file_name = boundaries_file_props[CONFIG_BOUNDARIES_FILE_NAME_FIELD].removesuffix('.geojson')
        boundary_column_name = boundaries_file_props[CONFIG_BOUNDARIES_COLUMN_FIELD]
        boundary_gdf = gpd.read_file(f'{input_path}/{boundary_file_name}.geojson')
        if grid_gdf.crs != boundary_gdf.crs:
            grid_gdf = grid_gdf.to_crs(boundary_gdf.crs)
        joined = gpd.sjoin(grid_gdf, boundary_gdf[[boundary_column_name, 'geometry']], how='left', predicate='intersects')
        joined = joined.drop_duplicates(subset=config[CONFIG_GRID_ID_COLUMN])
        grid_gdf.loc[joined.index, boundary_column_name] = joined[boundary_column_name].values
        grid_gdf.rename(
            columns={
                boundary_column_name: boundary_file_name
            },
            inplace=True
        )
    return grid_gdf

def assign_additional_data(grid_gdf, config, input_path):
    grid_population_column_name = config[CONFIG_GRID_POPULATION_COLUMN]
    for additional_data_file_props in config[CONFIG_ADDITIONAL_DATA_PROPS]:
        additional_data_file_name = additional_data_file_props[CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD].removesuffix('.csv')
        grid_location_column_name = additional_data_file_props[CONFIG_ADDITIONAL_DATA_GRID_LOCATION_COLUMN_FIELD]
        df = pd.read_csv(f'{input_path}/grid_additional_data/{additional_data_file_name}.csv')

        location_values = df[[additional_data_file_props[CONFIG_ADDITIONAL_DATA_LOCATION_COLUMN_FIELD], additional_data_file_props[CONFIG_ADDITIONAL_DATA_VALUE_COLUMN_FIELD]]].dropna()

        location_to_value = dict(zip(location_values[additional_data_file_props[CONFIG_ADDITIONAL_DATA_LOCATION_COLUMN_FIELD]], location_values[ additional_data_file_props[CONFIG_ADDITIONAL_DATA_VALUE_COLUMN_FIELD]]))

        grid_gdf[additional_data_file_name] = grid_gdf[grid_location_column_name].map(location_to_value)

        if additional_data_file_props[CONFIG_ADDITIONAL_DATA_NORMALIZE_FIELD] == False:
            continue
        
        normalized_mapping = {}
        total_location_pop = grid_gdf.groupby(grid_location_column_name)[grid_population_column_name].sum()
        for location, value in location_to_value.items():
            pop = total_location_pop.get(location)
            if pd.notna(pop) and pop > 0:
                normalized_mapping[location] = value / pop * 100

        grid_gdf[additional_data_file_name] = grid_gdf[grid_location_column_name].map(normalized_mapping)
        grid_gdf[additional_data_file_name] = grid_gdf[additional_data_file_name] * grid_gdf[grid_population_column_name]

    return grid_gdf

def normalize_grid_data(grid_gdf, config):
    pop_column = config[CONFIG_GRID_POPULATION_COLUMN]

    for column in config[CONFIG_GRID_EXISTING_COLUMNS]:
        if column in config[CONFIG_GRID_ALREADY_NORMALIZED_COLUMNS]:
            continue
        grid_gdf[column] = (
            grid_gdf[column] / grid_gdf[pop_column] * 100
        ).where(grid_gdf[pop_column] != 0, 0)


def process_grid(config, processed_path, input_path):
    grid_gdf = gpd.read_file(f'{input_path}/{config[CONFIG_GRID_FILE_NAME]}')
    grid_gdf = assign_grid_boundaries(grid_gdf=grid_gdf, config=config, input_path=input_path)
    normalize_grid_data(grid_gdf=grid_gdf, config=config)
    grid_gdf = assign_additional_data(grid_gdf=grid_gdf, config=config, input_path=input_path)
    grid_gdf.to_file(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_GRID_FILE_NAME}', driver='GeoJSON')

    