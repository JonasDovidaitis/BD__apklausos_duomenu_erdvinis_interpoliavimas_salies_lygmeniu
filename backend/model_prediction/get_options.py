import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from constants import CONFIG_SURVEY_ENCODING, CONFIG_SURVEY_FILE_NAME, CONFIG_SURVEY_FOLDER, CONFIG_DEMOGRAPHIC_COLUMNS

def get_options(config_file_name, input_path):
    with open(f'{input_path}/{config_file_name}', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    survey_df = pd.read_csv(f'{input_path}/{config[CONFIG_SURVEY_FOLDER]}/{config[CONFIG_SURVEY_FILE_NAME]}.csv', encoding=config[CONFIG_SURVEY_ENCODING])
    response = {}
    for demographic_column in config[CONFIG_DEMOGRAPHIC_COLUMNS]:
        if demographic_column in survey_df.columns:
            values = survey_df[demographic_column].dropna().unique().tolist()
            response[demographic_column] = sorted(values)
        else:
            response[demographic_column] = []
    return response