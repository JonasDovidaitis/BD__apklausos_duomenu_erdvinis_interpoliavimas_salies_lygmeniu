import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shutil
from examples.examples_constants import RAW_DATA_PATH, PREPARED_DATA_PATH

def clean_grid_additional_data():
    src_dir = f'{RAW_DATA_PATH}/grid_additional_data'
    dst_dir = f'{PREPARED_DATA_PATH}/grid_additional_data'

    os.makedirs(dst_dir, exist_ok=True)

    for filename in os.listdir(src_dir):
        src_path = os.path.join(src_dir, filename)
        dst_path = os.path.join(dst_dir, filename)

        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)


