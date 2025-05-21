import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import zipfile
from examples.examples_constants import PREPARED_DATA_PATH

def zip_prepared_data():
    folder_path = PREPARED_DATA_PATH
    zip_path = './backend/examples/prepared_zipped'
    zip_file = 'prepared_data.zip'
    os.makedirs(zip_path, exist_ok=True)
    with zipfile.ZipFile(f'{zip_path}/{zip_file}', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                rel_path = os.path.relpath(dir_path, start=folder_path) + '/'
                zip_info = zipfile.ZipInfo(rel_path)
                zipf.writestr(zip_info, '')

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, rel_path)
