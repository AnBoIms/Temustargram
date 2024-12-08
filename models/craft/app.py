from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from test import run_craft

app = Flask(__name__)
CORS(app)

STATIC_FOLDER = '/craft/static/cropped/sign'
logging.basicConfig(level=logging.INFO)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        app.logger.info("Received prediction request")
        image_files = [
            os.path.join(STATIC_FOLDER, f) for f in os.listdir(STATIC_FOLDER)
            if os.path.isfile(os.path.join(STATIC_FOLDER, f))
        ]
        if not image_files:
            return jsonify({"error": "No images found in static folder"}), 400

        results = []

        for image_path in image_files:
            file_name = os.path.basename(image_path)
            try:
                obj_id = int(file_name.split("_")[0])
            except ValueError:
                app.logger.error(f"Invalid file name format: {file_name}")
                continue

            try:
                #run craft
                polys = run_craft(image_path)

                polys_as_list = [poly.tolist() for poly in polys]

                results.append({
                    "id": obj_id,
                    "text_regions": polys_as_list
                })
                app.logger.info(f"Processed image: {file_name}")

            except Exception as e:
                app.logger.error(f"Error processing image {file_name}: {e}")
                continue

        return jsonify(results), 200

    except Exception as e:
        app.logger.error(f"Error in predict: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
