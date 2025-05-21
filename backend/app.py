import os
from flask import Flask, request, jsonify
from data_processing.zip_extract import extract_zip
from data_processing.process_data import process_data
from model_training.train import train_models
from model_prediction.get_options import get_options
from model_prediction.predict import make_predictions
from flask_cors import CORS
from constants import INPUT_PATH, PROCESSED_PATH, TRAINED_MODELS_PATH, PREDICTIONS_PATH

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'input')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
input_path = os.path.join(os.path.dirname(__file__), INPUT_PATH)

processed_path = os.path.join(os.path.dirname(__file__), PROCESSED_PATH)
trained_models_path = os.path.join(os.path.dirname(__file__), TRAINED_MODELS_PATH)
predictions_path = os.path.join(os.path.dirname(__file__), PREDICTIONS_PATH)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not file.filename.endswith('.zip'):
        return jsonify({'message': 'Only .zip files are allowed'}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({'message': 'File uploaded successfully', 'file_path': save_path})

@app.route('/extract', methods=['POST'])
def extract():
    params = request.json
    zip_file_name = params.get('zip_file')
    zip_path = os.path.join(os.path.dirname(__file__), INPUT_PATH)
    extract_zip(f'{zip_path}/{zip_file_name}', zip_path)
    return jsonify({ 'message': 'Data extracted successfully' })

@app.route('/prepare', methods=['POST'])
def prepare():
    params = request.json
    config_file_name = params.get('config_file')
    process_data(config_file_name, input_path=input_path, processed_path=processed_path)
    return jsonify({ 'message': 'Data processed successfully' })

@app.route('/train', methods=['POST'])
def train():
    params = request.json
    config_file_name = params.get('config_file')
    train_models(config_file_name, input_path=input_path, processed_path=processed_path, trained_models_path=trained_models_path)
    return jsonify({ 'message': 'Model trained successfully' })

@app.route('/options', methods=['POST'])
def options():
    params = request.json
    config_file_name = params.get('config_file')
    response = get_options(config_file_name, input_path=input_path)
    return jsonify(response)

@app.route('/predict', methods=['POST'])
def predict():
    params = request.json
    config_file_name = params.get('config_file')
    values = params.get('values')
    make_predictions(config_file_name, input_path=input_path, processed_path=processed_path, trained_models_path=trained_models_path, predictions_path=predictions_path, demographic_values=values)
    return jsonify({ 'message': 'Predictions made successfully' })

if __name__ == '__main__':
    app.run(debug=True)