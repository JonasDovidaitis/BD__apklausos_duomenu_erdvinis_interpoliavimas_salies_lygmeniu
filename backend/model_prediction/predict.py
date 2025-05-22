import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import pandas as pd
import torch
import numpy as np
import geopandas as gpd
from model_training.train_gnn import GNNClassifier
from model_training.train_gnn_regression import GNNRegressor
from sklearn.neighbors import NearestNeighbors
from model_training.train import get_training_columns
from model_prediction.get_options import get_options
from constants import CONFIG_GRID_ID_COLUMN, CONFIG_COLUMN_TO_PREDICT, CONFIG_DEMOGRAPHIC_MAPPINGS, CONFIG_IS_CLASSIFICATION, CONFIG_SURVEY_ENCODING, CONFIG_SURVEY_FILE_NAME, GNN_MODEL_FILE_NAME, GNN_SCALER_FILE_NAME, PROCESSED_GRID_FILE_NAME, PROCESSED_SURVEY_FILE_NAME, RF_MODEL_FILE_NAME, SVM_MODEL_FILE_NAME, SVM_SCALER_FILE_NAME
    
def get_gnn_predictions(config, survey_df, valid_gdf, X, trained_models_path):
    gnn_scaler = joblib.load(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{GNN_SCALER_FILE_NAME}')
    X_scaled = gnn_scaler.transform(X)
    gnn_model_path = f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{GNN_MODEL_FILE_NAME}'
    isClassification = config[CONFIG_IS_CLASSIFICATION]
    
    if isClassification:
        gnn_model = GNNClassifier(
            input_dim=X_scaled.shape[1],
            hidden_dim=128,
            num_classes=len(survey_df[config[CONFIG_COLUMN_TO_PREDICT]].unique())
        )
    else:
        gnn_model = GNNRegressor(
            input_dim=X_scaled.shape[1],
            hidden_dim=128,
            output_dim=1
        )
    gnn_model.load_state_dict(torch.load(gnn_model_path, map_location='cpu'))
    gnn_model.eval()

    coords = np.array(list(zip(valid_gdf.geometry.centroid.x, valid_gdf.geometry.centroid.y)))
    nbrs = NearestNeighbors(n_neighbors=6).fit(coords)
    _, indices = nbrs.kneighbors(coords)
    edges = [[i, j] for i, neighbors in enumerate(indices) for j in neighbors if i != j]
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    with torch.no_grad():
        if isClassification:
            gnn_logits = gnn_model(X_tensor, edge_index)
            preds_gnn = torch.argmax(gnn_logits, dim=1).numpy()
        else:
            preds_gnn = gnn_model(X_tensor, edge_index).numpy()
    return preds_gnn

def get_columns(config, options, values):
    demographic_mappings = config[CONFIG_DEMOGRAPHIC_MAPPINGS]
    result = {}
    for column in options:
        if column not in values:
            continue
        if column in demographic_mappings:
            result[column] = demographic_mappings[column].index(values[column]) + 1
        else:
            for column_value in options[column]:
                result[column_value] = int(values[column] == column_value)
    return result

def make_predictions(config_file_name, input_path, processed_path, trained_models_path, predictions_path, demographic_values):
    with open(f'{input_path}/{config_file_name}', 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    survey_df = pd.read_csv(f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_SURVEY_FILE_NAME}', encoding=config[CONFIG_SURVEY_ENCODING])

    options = get_options(config_file_name, input_path)
    columns_to_append = get_columns(config, options, demographic_values)
    
    grid_path = f'{processed_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{PROCESSED_GRID_FILE_NAME}'
    grid_gdf = gpd.read_file(grid_path)

    required_columns = list(demographic_values.values())
    mask = grid_gdf[required_columns[0]] > 0
    for col in required_columns[1:]:
        mask &= grid_gdf[col] > 0
    valid_gdf = grid_gdf[mask].copy()

    for column, value in columns_to_append.items():
        valid_gdf[column] = value

    training_columns = get_training_columns(config)
    X = valid_gdf[training_columns]

    rf_model = joblib.load(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{RF_MODEL_FILE_NAME}')

    preds_rf = rf_model.predict(X)

    preds_gnn = get_gnn_predictions(config=config, survey_df=survey_df, valid_gdf=valid_gdf, X=X, trained_models_path=trained_models_path)
    
    svm_model = joblib.load(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{SVM_MODEL_FILE_NAME}')
    svm_scaler = joblib.load(f'{trained_models_path}/{config[CONFIG_SURVEY_FILE_NAME]}/{SVM_SCALER_FILE_NAME}')
    X_scaled = svm_scaler.transform(X)
    preds_svm = svm_model.predict(X_scaled)

    grid_gdf['prediction_rf'] = -1
    grid_gdf['prediction_svm'] = -1
    grid_gdf['prediction_gnn'] = -1

    grid_gdf.loc[mask, 'prediction_rf'] = preds_rf
    grid_gdf.loc[mask, 'prediction_svm'] = preds_svm
    grid_gdf.loc[mask, 'prediction_gnn'] = preds_gnn

    columns_to_save = [config[CONFIG_GRID_ID_COLUMN], 'prediction_rf', 'prediction_svm', 'prediction_gnn', 'geometry']
    output_gdf = grid_gdf[columns_to_save].copy()
    output_path = f'{predictions_path}/{config[CONFIG_SURVEY_FILE_NAME]}/predictions.geojson'
    os.makedirs(f'{predictions_path}/{config[CONFIG_SURVEY_FILE_NAME]}', exist_ok=True)
    output_gdf.to_file(output_path, driver='GeoJSON')
