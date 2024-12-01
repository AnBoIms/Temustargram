from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
import os
import shutil

app = Flask(__name__)
CORS(app)

# 디렉토리 설정
DOWNLOAD_FOLDER = './downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_path = data.get("image_path")
    if not image_path:
        return jsonify({"error": "No image_path provided"}), 400

    try:
        response = requests.get(image_path, stream=True)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 400
        
        file_name = os.path.basename(image_path)
        local_image_path = os.path.join(DOWNLOAD_FOLDER, file_name)

        with open(local_image_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        app.logger.info(f"Image downloaded and saved as {local_image_path}")
    except Exception as e:
        app.logger.error(f"Error downloading image: {e}")
        return jsonify({"error": "Error downloading image"}), 500

    # MMDetection 로직 수행
    detection_output = """
    901 2091,1156 1687,1800 2095,1546 2498
    """  # Dummy 데이터

    objects_data = []
    lines = detection_output.strip().split("\n")
    for idx, line in enumerate(lines, start=1):
        coords = [list(map(int, pair.split())) for pair in line.split(",")]
        objects_data.append({
            "id": idx,
            "type": "id_card",
            "polygon": coords
        })

    response_data = jsonify(objects_data)

    try:
        os.remove(local_image_path)
        app.logger.info(f"Image file {local_image_path} deleted after response")
    except Exception as e:
        app.logger.error(f"Error deleting image file: {e}")

    return response_data, 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
