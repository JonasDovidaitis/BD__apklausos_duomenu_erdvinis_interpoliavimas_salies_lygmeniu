Bachelor's work `Country Level Spatial Inference of Survey Data` code and guide.

## Usage

To start the frontend run: `npm run dev` from `\frontend` folder.
To start the backend run: `py app.py` from `\backend` folder.

Open `http://localhost:5173/` in the browser.

Application consists of two parts:

## frontend

Frontend is responsible for UI layer of the application. It allows user to interact with the backend processes. It is also responsible for displaying model predictions made on grid data.

## backend

Backend consists of these parts:
1. `backend\data_processing`:
   - Adds additional demographic data and territories to grid data.
   - Appends grid data to survey data and encodes preexisting survey data.
   - At the end processed data is saved under `backend\data\processed`.
2. `backend\model_training`:
   - Trains Graph Neural Network, Random forest and Support Vector machine models using processed data.
   - Saves trained models under `backend\data\trained_models`
3. `backend\model_prediction`:
   - Uses trained models to make predictions for grid data.
   - Predicted classes are saved under `backend\data\predictions`

Also, `backend\examples` contains examples of how to format raw data. Those examples cannot be used using UI, instead each file has to be executed separately.

## Configuration file

Example configuration files can be found under `backend\examples\raw_data\surveys`, they are named `config.json`.
Configuration file is needed in order for the backend to work.

- `survey_file_name` - name of the survey data file without suffix (file in csv format).
- `survey_folder_name` - name of the folder containing the survey data.
- `survey_encoding` - encoding of the survey data file. This is needed to properly extract the survey data.
- `grid_file_name` - name of the grid file (file in geojson format).
- `column_to_predict` - name of the column to be used for predictions.
- `grid_existing_columns` - columns of the grids that can be added to the survey data.
- `grid_already_normalized_columns` - grid columns that do not need to be normalized (e.g. mean_age).
- `grid_id` - unique identification column of the grids.
- `pop_column` - population column of the grids.
- `boundaries` - administrative area files and the column names in them.
- `demographic_columns` - demographic columns of the survey.
- `location_columns` - names of the columns of the survey data that contain the place of residence of the respondents (e.g. municipality).
- `additional_data` - names of the additional data files, for each file it is necessary to specify the columns of the file to be used and whether the data in the file should be normalized.
- `demographic_mappings` - demographic columns that do not require one-hot encoding.