import os
import time
import sys
import requests
from zipfile import ZipFile
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from utility.utility import setup_logging,format_time
import json

def download_zip_file(url, output_dir):
    response = requests.get(url, stream=True)
    os.makedirs(output_dir, exist_ok=True)

    if response.status_code == 200:
        filename = os.path.join(output_dir, "downloaded.zip")
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Downloaded zip file: {filename}")
        return filename
    else:
        raise Exception(f"Failed to download file: Status code {response.status_code}")

def extract_zip_file(zip_filename, output_dir):
    with ZipFile(zip_filename, "r") as zip_file:
        zip_file.extractall(output_dir)
    logger.info(f"Extracted files written to: {output_dir}")
    logger.info("Removing the zip file")
    os.remove(zip_filename)

def fix_json_dict(output_dir):
    file_path = os.path.join(output_dir, 'dict_artists.json')
    fixed_file_path = os.path.join(output_dir, 'fixed_da.json')

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(fixed_file_path, "w", encoding="utf-8") as f_out:
        for key, value in data.items():
            record = {"id": key, "related_ids": value}
            json.dump(record, f_out, ensure_ascii=False)
            f_out.write("\n")

    logger.info(f"File {file_path} has been fixed and written to {fixed_file_path}")
    logger.info("Removing the original file")
    os.remove(file_path)

# Entry point
if __name__ == "__main__":
    logger = setup_logging("extract.log")
    if len(sys.argv) < 2:
        logger.warning("Extraction path is required")
        logger.warning("Example Usage:")
        logger.warning("python3 execute.py /home/username/Data/Extraction")
    else:
        try:
            logger.info("Starting Extraction Engine...")
            start=time.time()
            EXTRACT_PATH = sys.argv[1]
            KAGGLE_URL = "https://www.kaggle.com/api/v1/datasets/download/yamaerenay/spotify-dataset-19212020-600k-tracks"

            zip_filename = download_zip_file(KAGGLE_URL, EXTRACT_PATH)
            extract_zip_file(zip_filename, EXTRACT_PATH)
            fix_json_dict(EXTRACT_PATH)

            logger.info("Extraction Successfully Completed!!!")
            end=time.time()
            logger.info( logger.info(f"Total time taken{format_time(end-start)}"))
        except Exception as e:
            logger.warning(f"Error: {e}")