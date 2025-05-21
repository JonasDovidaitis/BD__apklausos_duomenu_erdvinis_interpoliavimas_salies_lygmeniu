import numpy as np
import pandas as pd
import geopandas as gpd
import random 
from shapely.geometry import Point

from constants import CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD, CONFIG_ADDITIONAL_DATA_PROPS, CONFIG_DEMOGRAPHIC_COLUMNS, CONFIG_DEMOGRAPHIC_MAPPINGS, CONFIG_GRID_EXISTING_COLUMNS, CONFIG_GRID_ID_COLUMN, CONFIG_GRID_POPULATION_COLUMN, CONFIG_LOCATION_COLUMNS, CONFIG_SURVEY_ENCODING, CONFIG_SURVEY_FILE_NAME, CONFIG_SURVEY_FOLDER, GENERATED_POINT_COLUMN, PROCESSED_GRID_FILE_NAME, PROCESSED_SURVEY_FILE_NAME, SELECTED_GRID_COLUMN

def get_location_boundaries(location_boundaries_gdf, location_column_name, location_name):
    return location_boundaries_gdf[location_boundaries_gdf[location_column_name] == location_name]

def filter_grid_by_demographics(grid_gdf, demographic_data_column_names):
    filtered_gdf = grid_gdf.loc[grid_gdf[demographic_data_column_names].gt(0).all(axis=1)]
    return filtered_gdf

def get_grids_in_location(grid_gdf, row, column_names):
    for column_name in column_names:
        if column_name in grid_gdf.columns:
            row_value = row[column_name]
            if pd.isna(row_value) or row_value == '':
                continue

            grids_in_location_boundaries = grid_gdf[grid_gdf[column_name] == row_value]
            if not grids_in_location_boundaries.empty:
                return grids_in_location_boundaries


def get_weights(grids_gdf, demographic_data_column_names, population_column):
    total_product = 1
    for col in demographic_data_column_names:
        ratio = grids_gdf[col] / grids_gdf[population_column]
        total_product *= ratio

    weights = np.ceil(total_product * grids_gdf[population_column]).astype(int)
    return weights

def select_random_grid(grids_gdf, demographic_data_column_names, population_column):
    weights = get_weights(grids_gdf, demographic_data_column_names, population_column)
    selected_grid = grids_gdf.sample(weights=weights)
    
    return selected_grid.iloc[0]

def generate_random_point_within_grid(selected_grid):
    x_min, y_min, x_max, y_max = selected_grid.geometry.bounds
    x = random.uniform(x_min, x_max)
    y = random.uniform(y_min, y_max)
    return Point(x, y)

def assign_random_point_to_survey_dataframe(survey_df, grid_gdf, demographic_data_column_names, location_column_names, grid_id_column, grid_population_column):
    points = []
    selected_grids = []
    for _, row in survey_df.iterrows():
      grid_demographic_data_column_names = row[demographic_data_column_names]
      grid_demographic_data_columns_without_na = [val for val in grid_demographic_data_column_names if pd.notna(val) and str(val).strip() != ""]
      filtered_grid_gdf = filter_grid_by_demographics(grid_gdf, grid_demographic_data_columns_without_na) if len(grid_demographic_data_columns_without_na) > 0 else grid_gdf

      grids_in_location_boundaries_gdf = get_grids_in_location(grid_gdf=filtered_grid_gdf, row=row, column_names=location_column_names)

      if grids_in_location_boundaries_gdf.empty:
          points.append(None)
          selected_grids.append(None)
          continue
      
      selected_grid = select_random_grid(grids_in_location_boundaries_gdf, grid_demographic_data_columns_without_na, grid_population_column)

      if selected_grid is None:
          points.append(None)
          continue

      random_point = generate_random_point_within_grid(selected_grid)
      points.append(random_point)
      selected_grids.append(selected_grid[grid_id_column])
  
    survey_df[GENERATED_POINT_COLUMN] = points
    survey_df[SELECTED_GRID_COLUMN] = selected_grids
    return survey_df

def append_grid_data_to_survey_df(grid_gdf, survey_df, columns_to_append, grid_id_column):
    survey_df = survey_df.merge(
        grid_gdf[[grid_id_column] + columns_to_append],
        left_on=SELECTED_GRID_COLUMN,
        right_on=grid_id_column,
        how='left'
    )
    survey_df.drop(columns=[grid_id_column], inplace=True)
    return survey_df

def encode_columns(survey_df, demographic_columns, demographic_mappings):
    columns_to_one_hot = []
    for column in demographic_columns:
        if column in demographic_mappings:
            value_to_index = {val: idx + 1 for idx, val in enumerate(demographic_mappings[column])}
            survey_df[column] = survey_df[column].map(value_to_index)
            continue
        columns_to_one_hot.append(column)
    if len(columns_to_one_hot) == 0:
        return survey_df
    survey_df = pd.get_dummies(survey_df, columns=columns_to_one_hot, prefix='', prefix_sep='', dtype=int)
    return survey_df

def process_survey(config, input_path, processed_path):
    survey_df = pd.read_csv(f'{input_path}/{config[CONFIG_SURVEY_FOLDER]}/{config[CONFIG_SURVEY_FILE_NAME]}.csv', encoding=config[CONFIG_SURVEY_ENCODING])
    grid_gdf = gpd.read_file(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_GRID_FILE_NAME}')
    location_column_names = config[CONFIG_LOCATION_COLUMNS]
    demographic_data_column_names = config[CONFIG_DEMOGRAPHIC_COLUMNS]
    grid_id_column = config[CONFIG_GRID_ID_COLUMN]
    grid_population_column = config[CONFIG_GRID_POPULATION_COLUMN]
    assign_random_point_to_survey_dataframe(
        survey_df=survey_df,
        grid_gdf=grid_gdf,
        demographic_data_column_names=demographic_data_column_names,
        location_column_names=location_column_names,
        grid_id_column=grid_id_column,
        grid_population_column=grid_population_column)
    
    grid_appended_columns = []
    for additional_data_file_props in config[CONFIG_ADDITIONAL_DATA_PROPS]:
        column_name = additional_data_file_props[CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD].removesuffix('.csv')
        grid_appended_columns.append(column_name)

    columns_to_append = [config[CONFIG_GRID_POPULATION_COLUMN], *config[CONFIG_GRID_EXISTING_COLUMNS], *grid_appended_columns]
    survey_df = append_grid_data_to_survey_df(
        grid_gdf=grid_gdf,
        survey_df=survey_df,
        grid_id_column=grid_id_column,
        columns_to_append=columns_to_append 
    )
    survey_df = encode_columns(survey_df=survey_df, demographic_columns=demographic_data_column_names, demographic_mappings=config[CONFIG_DEMOGRAPHIC_MAPPINGS])
    survey_df.to_csv(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_SURVEY_FILE_NAME}', index=False, encoding=config[CONFIG_SURVEY_ENCODING])