import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pandas as pd
from constants import CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD, CONFIG_ADDITIONAL_DATA_PROPS, CONFIG_COLUMN_TO_PREDICT, CONFIG_DEMOGRAPHIC_COLUMNS, CONFIG_DEMOGRAPHIC_MAPPINGS, CONFIG_GRID_EXISTING_COLUMNS, CONFIG_GRID_POPULATION_COLUMN, CONFIG_IS_CLASSIFICATION, CONFIG_SURVEY_ENCODING, CONFIG_SURVEY_FILE_NAME, CONFIG_SURVEY_FOLDER, GNN_METRICS_FILE_NAME, GNN_MODEL_FILE_NAME, GNN_SCALER_FILE_NAME, INPUT_PATH, PROCESSED_PATH, PROCESSED_SURVEY_FILE_NAME, RF_METRICS_FILE_NAME, RF_MODEL_FILE_NAME, SVM_METRICS_FILE_NAME, SVM_MODEL_FILE_NAME, SVM_SCALER_FILE_NAME, TRAINED_MODELS_PATH
from model_training.train_gnn import train_graph_neural_network
from model_training.train_rf import train_random_forest
from model_training.train_svm import train_support_vector_machine
from model_training.train_rf_regression import train_random_forest_regression
from model_training.train_svm_regression import train_support_vector_regression
from model_training.train_gnn_regression import train_gnn_regression
import joblib
import torch

def get_training_columns(config):
    survey_df_original = pd.read_csv(f'{INPUT_PATH}/{config[CONFIG_SURVEY_FOLDER]}/{config[CONFIG_SURVEY_FILE_NAME]}.csv', encoding=config[CONFIG_SURVEY_ENCODING])
    grid_appended_columns = []
    for additional_data_file_props in config[CONFIG_ADDITIONAL_DATA_PROPS]:
        column_name = additional_data_file_props[CONFIG_ADDITIONAL_DATA_FILE_NAME_FIELD].removesuffix('.csv')
        grid_appended_columns.append(column_name)
    
    demographic_columns = config[CONFIG_DEMOGRAPHIC_COLUMNS]
    demographic_mappings = config[CONFIG_DEMOGRAPHIC_MAPPINGS]
    columns_to_train = [config[CONFIG_GRID_POPULATION_COLUMN], *config[CONFIG_GRID_EXISTING_COLUMNS], *grid_appended_columns]
    for column in demographic_columns:
        if column in demographic_mappings:
            columns_to_train.append(column)
            continue
        columns_to_train += [*survey_df_original[column].unique()]
    columns_to_train = [col for col in columns_to_train if isinstance(col, str)]
    columns_to_train.sort()
    return columns_to_train  


def train_models(config_file_name, input_path, processed_path, trained_models_path):
    with open(f'{input_path}/{config_file_name}', 'r', encoding='utf-8') as f:
        config = json.load(f)
    os.makedirs(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}', exist_ok=True)
    isClassification = config[CONFIG_IS_CLASSIFICATION]

    training_columns = get_training_columns(config=config)
    survey_df = pd.read_csv(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_SURVEY_FILE_NAME}', encoding=config[CONFIG_SURVEY_ENCODING])
    X = survey_df[training_columns]
    y = survey_df[config[CONFIG_COLUMN_TO_PREDICT]]
    if isClassification:
        rf_result = train_random_forest(X, y, useBalanced=True)
    else:
        rf_result = train_random_forest_regression(X, y)
    joblib.dump(rf_result['model'], f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{RF_MODEL_FILE_NAME}')
    df = pd.DataFrame([rf_result['metrics']])
    df.to_csv(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{RF_METRICS_FILE_NAME}', index=False)

    if isClassification:
        svm_result = train_support_vector_machine(X, y, useBalanced=True)
    else:
        svm_result = train_support_vector_regression(X, y)
    joblib.dump(svm_result['model'], f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{SVM_MODEL_FILE_NAME}')
    joblib.dump(svm_result['scaler'], f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{SVM_SCALER_FILE_NAME}')
    df = pd.DataFrame([svm_result['metrics']])
    df.to_csv(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{SVM_METRICS_FILE_NAME}', index=False)

    if isClassification:
        gnn_result = train_graph_neural_network(config, survey_df, training_columns)
    else:
        gnn_result = train_gnn_regression(config, survey_df, training_columns)
    torch.save(gnn_result['model'].state_dict(), f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{GNN_MODEL_FILE_NAME}')
    joblib.dump(gnn_result['scaler'], f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{GNN_SCALER_FILE_NAME}')
    df = pd.DataFrame([gnn_result['metrics']])
    df.to_csv(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{GNN_METRICS_FILE_NAME}', index=False)