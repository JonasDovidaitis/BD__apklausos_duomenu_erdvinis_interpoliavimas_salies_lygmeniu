import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from examples.clean_depression_data import clean_depression_data
from examples.clean_food_data import clean_food_data
from examples.clean_grid_additional_data import clean_grid_additional_data
from examples.clean_location_data import clean_location_data
from examples.clean_grid_data import clean_grid_data
from examples.create_zip import zip_prepared_data

def clean_raw_data():
    clean_depression_data()
    print('Depression survey cleaned')
    clean_food_data()
    print('Food survey cleaned')
    clean_grid_additional_data()
    print('Grid additional data cleaned')
    clean_location_data()
    print('Location data cleaned')
    clean_grid_data()
    print('Grid data cleaned')
    zip_prepared_data()
    print('Zip created')
clean_raw_data()