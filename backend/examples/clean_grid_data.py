import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import geopandas as gpd
from examples.examples_constants import RAW_DATA_PATH, PREPARED_DATA_PATH

AGE_COLUMNS = ['all_15_19','all_20_24','all_25_29','all_30_34','all_35_39','all_40_44','all_45_49','all_50_54','all_55_59','all_60_64','all_65_69','all_70_74','all_75_79','all_80_84', 'all_85_plius', 'all_00_04','all_05_09','all_10_14',]
OCP_COLUMNS = ['OCP_self','OCP_employer','OCP_other','OCP_employees']
EDUC_COLUMNS = ['EDUC_H_all', 'EDUC_PS_all', 'EDUC_S_all', 'EDUC_B_all', 'EDUC_P_all', 'EDUC_UP_all']
EDUC_MALE_COLUMNS = ['EDUC_H_males', 'EDUC_PS_males', 'EDUC_S_males', 'EDUC_B_males', 'EDUC_P_males', 'EDUC_UP_males']
EDUC_FEMALE_COLUMNS = ['EDUC_H_female', 'EDUC_PS_female', 'EDUC_S_female', 'EDUC_B_female', 'EDUC_P_female', 'EDUC_UP_female']
PRF_COLUMNS = ['PRF_managers', 'PRF_professionals', 'PRF_TAprofessionals', 'PRF_clerics', 'PRF_agrivulture', 'PRF_craft', 'PRF_elementary', 'PRF_armed', 'PRF_operators', 'PRF_service']
ACT_COLUMNS = ['ACT_employees', 'ACT_unemployed', 'ACT_pension', 'ACT_student', 'ACT_other']
ECNM_COLUMNS = ['ECNM_A', 'ECNM_BCDE', 'ECNM_F', 'ECNM_G', 'ECNM_H', 'ECNM_IJ', 'ECNM_KL', 'ECNM_M', 'ECNM_N', 'ECNM_P', 'ECNM_Q', 'ECNM_RSTU']
MARRG_COLUMNS = ['MARRG_STAT_DIVORCED', 'MARRG_STAT_WIDOW', 'MARRG_STAT__MARRIED', 'MARRG_STAT_UNMARRIED']
BCOUNTRY_COLUMNS = ['BCOUTRY_LTU', 'BCOUTRY_ASIA_POST', 'BCOUTRY_EU', 'BCOUTRY_BLR', 'BCOUTRY_RUS', 'BCOUTRY_UKR', 'BCOUTRY_BC', 'BCOUTRY_OTHER']
NAC_COLUMNS = ['NAC_LT', 'NAC_OTH']
BIRTH_COLUMNS = ['BIRTH_URBAN', 'BIRTH_RURAL', 'BIRTH_OUT']
MIGR_COLUMNS = ['MIGR_CHANGE', 'MIGR_SAME']
POPULATION_COLUMN = 'POP'

def get_correct_population(row):
  if row[POPULATION_COLUMN] > 3:
    return row[POPULATION_COLUMN]
  expected_pop=1
  if row['havt_children_15plius_percent'] > 30 and row['havt_children_15plius_percent'] < 40:
    return 3
  if row['havt_children_15plius_percent'] > 60 and row['havt_children_15plius_percent'] < 70:
    return 3
  if row['MALE'] == 9 and row['havt_children_15plius_percent'] > 1 and row['havt_children_15plius_percent'] < 99:
    return 3
  if row['havt_children_15plius_percent'] == 50:
    return 2
  if row['MALE'] == 9 and row['FEMALE'] == 9:
    expected_pop = 2
  if row['BIRTH_URBAN'] == 9 and row['BIRTH_RURAL'] == 9:
    expected_pop = 2
  if row['MIGR_CHANGE'] == 9 and row['MIGR_SAME'] == 9:
    expected_pop = 2

  meanAgeDecimal = row['mean_age'] - int(row['mean_age'])

  if meanAgeDecimal > 0.4 and meanAgeDecimal < 0.6:
      expected_pop = 2
  elif meanAgeDecimal > 0:
    return 3

  for column_names in [AGE_COLUMNS, OCP_COLUMNS, [*EDUC_MALE_COLUMNS, *EDUC_FEMALE_COLUMNS], PRF_COLUMNS, ACT_COLUMNS, ECNM_COLUMNS, MARRG_COLUMNS, BCOUNTRY_COLUMNS]:
    pop_sum = 0
    for column in column_names:
      pop_sum = pop_sum + row[column]
    if pop_sum > 9:
      if pop_sum > 18:
        return 3
      expected_pop = 2

  return expected_pop

def adjust_group_numbers(row, columns, population):
  population_left = population
  columns_with_incorrect_numbers = []
  for column in columns:
    if row[column] > 9:
      population_left -= row[column]
    elif row[column] == 9:
      columns_with_incorrect_numbers.append(column)
  if len(columns_with_incorrect_numbers) == 0:
    return

  population_left = max(population_left, len(columns_with_incorrect_numbers))
  base = int(population_left / len(columns_with_incorrect_numbers))
  population_left = population_left - (base * len(columns_with_incorrect_numbers))
  for column in columns_with_incorrect_numbers:
    row[column] = base
    if population_left > 0:
      row[column] += 1
      population_left -= 1

def adjust_incorrect_numbers_in_columns(grid_gdf):
  grid_gdf.replace('', 0, inplace=True)
  grid_gdf.fillna(0, inplace=True) 
  adjusted_rows = []
  for _, row in grid_gdf.iterrows():
    correct_pop = get_correct_population(row)
    row[POPULATION_COLUMN] = correct_pop
    for columnNames in [AGE_COLUMNS, ['MALE', 'FEMALE'], BIRTH_COLUMNS, MIGR_COLUMNS, NAC_COLUMNS, BCOUNTRY_COLUMNS]:
      adjust_group_numbers(row, columnNames, correct_pop)

    correct_pop = correct_pop - row['all_00_04'] - row['all_05_09']
    adjust_group_numbers(row, EDUC_COLUMNS, correct_pop)
    correct_pop = correct_pop - row['all_10_14']

    adjust_group_numbers(row, ACT_COLUMNS, correct_pop)

    adjust_group_numbers(row, OCP_COLUMNS, row['ACT_employees'])
    adjust_group_numbers(row, PRF_COLUMNS, row['ACT_employees'])
    adjust_group_numbers(row, ECNM_COLUMNS, row['ACT_employees'])
    adjust_group_numbers(row, MARRG_COLUMNS, correct_pop)
    adjusted_rows.append(row)
  
  new_gdf = gpd.GeoDataFrame(adjusted_rows)

  if 'geometry' in new_gdf.columns:
      new_gdf.set_geometry('geometry', inplace=True)
  new_gdf.set_crs(grid_gdf.crs, inplace=True)
  return  new_gdf

redundant_columns = [
    'all_00_04', 'all_05_09', 'all_10_14', 'all_80_84', 'all_85_plius',
    'all_00_14', 'all_15_64', 'all_65_plius',
    'males_00_14', 'males_15_64', 'males_65_plius',
    'females_00_14', 'females_15_64', 'females_65_plius',
    'adults', 'adults_males', 'adults_females',
    'youngest_firstbirth_mother', 'oldest_firstbirth_mother',
    'EDUC_H_males', 'EDUC_PS_males', 'EDUC_S_males', 'EDUC_B_males', 'EDUC_P_males', 'EDUC_UP_males',
    'EDUC_H_female', 'EDUC_PS_female', 'EDUC_S_female', 'EDUC_B_female', 'EDUC_P_female', 'EDUC_UP_female',
    'BCOUTRY_ASIA_POST', 'BCOUTRY_EU', 'BCOUTRY_BLR', 'BCOUTRY_RUS', 'BCOUTRY_UKR', 'BCOUTRY_BC', 'BCOUTRY_OTHER',
    'MARRG_STAT_DIVORCED_MALE', 'MARRG_STAT_WIDOW_MALE', 'MARRG_STAT__MARRIED_MALE', 'MARRG_STAT_UNMARRIED_MALE',
    'MARRG_STAT_DIVORCED_FEMALE', 'MARRG_STAT_WIDOW_FEMALE', 'MARRG_STAT__MARRIED_FEMALE', 'MARRG_STAT_UNMARRIED_FEMALE',
    'BIRTH_OUT',
    'Shape__Area', 'Shape__Length', 'OBJECTID'
]

def clean_grid_data():
  grid_gdf = gpd.read_file(f'{RAW_DATA_PATH}/gyventoju_surasymas2021.geojson')
  updated_grid_gdf = adjust_incorrect_numbers_in_columns(grid_gdf=grid_gdf)
  updated_grid_gdf.drop(columns=redundant_columns, inplace=True)
  updated_grid_gdf.to_file(f'{PREPARED_DATA_PATH}/grid.geojson', driver='GeoJSON')
  return updated_grid_gdf
