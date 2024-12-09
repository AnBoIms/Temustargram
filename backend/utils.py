import os
import shutil
import logging

IMAGE_FOLDER = './static' 

def clear_static_directory(exclude_files=None):
    exclude_files = exclude_files or []
    for filename in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            if filename in exclude_files:
                logging.info(f"Skipped: {file_path}")
                continue
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) 
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            logging.info(f"Deleted: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {e}")
