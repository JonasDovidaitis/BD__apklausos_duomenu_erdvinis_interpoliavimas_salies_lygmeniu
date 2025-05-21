import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from constants import CONFIG_SURVEY_FILE_NAME
from data_processing.grid_processing import process_grid
from data_processing.survey_processing import process_survey

def process_data(config_file_name, input_path, processed_path):
    with open(f'{input_path}/{config_file_name}', 'r', encoding='utf-8') as f:
        config = json.load(f)

    os.makedirs(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}', exist_ok=True)
    process_grid(config, processed_path=processed_path, input_path=input_path)
    process_survey(config, input_path=input_path, processed_path=processed_path)