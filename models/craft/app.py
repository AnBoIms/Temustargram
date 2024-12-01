from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import requests
import shutil
from test import run_craft

app = Flask(__name__)
CORS(app)

# 디렉토리 설정
DOWNLOAD_FOLDER = './downloads'
RESULT_FOLDER = './result'

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])

def predict():
    try:
        objects = request.get_json()
        if not objects:
            return jsonify({"error": "No objects provided"}), 400

        results = []

        for obj in objects:
            obj_id = obj.get("id")
            cropped_image_path = obj.get("cropped_image_path")
            if not obj_id or not cropped_image_path:
                continue

            local_image_path = os.path.join(DOWNLOAD_FOLDER, f"cropped_{obj_id}.png")

            try:
                response = requests.get(cropped_image_path, stream=True)
                if response.status_code != 200:
                    app.logger.error(f"Failed to download image: {cropped_image_path}")
                    continue

                # file_name = f"cropped_{obj_id}.png"
                # local_image_path = os.path.join(DOWNLOAD_FOLDER, file_name)

                with open(local_image_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

                app.logger.info(f"Downloaded and saved image: {local_image_path}")
            except Exception as e:
                app.logger.error(f"Error downloading image: {cropped_image_path} - {e}")
                continue

            # # 2. 더미 텍스트 감지 결과 생성
            # dummy_text_regions = """
            # 118,54,403,52,403,103,118,105
            # 111,143,397,143,397,189,111,189
            # 83,212,439,212,439,252,83,252
            # 64,275,301,275,301,314,64,314
            # """
            

            # text_regions = []
            # for region in dummy_text_regions.strip().split("\n"):
            #     coords = list(map(int, region.split(",")))
            #     polygon = [coords[i:i+2] for i in range(0, len(coords), 2)]
            #     text_regions.append(polygon)

            # results.append({
            #     "id": obj_id,
            #     "text_regions": text_regions
            # })

            # try:
            #     os.remove(local_image_path)
            #     app.logger.info(f"Deleted image: {local_image_path}")
            # except Exception as e:
            #     app.logger.error(f"Error deleting image: {local_image_path} - {e}")
            try:
                polys = run_craft(local_image_path, RESULT_FOLDER)
                results.append({
                    "id": obj_id,
                    "text_regions": polys
                })
            except Exception as e:
                app.logger.error(f"Error running CRAFT for {obj_id}: {e}")
                continue

            try:
                os.remove(local_image_path)
            except Exception as e:
                app.logger.error(f"Error deleting image: {local_image_path} - {e}")

        return jsonify(results), 200

    except Exception as e:
        app.logger.error(f"Error in predict: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
