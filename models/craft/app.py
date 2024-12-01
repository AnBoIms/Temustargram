from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

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

            dummy_text_regions = """
            118,54,403,52,403,103,118,105
            111,143,397,143,397,189,111,189
            83,212,439,212,439,252,83,252
            64,275,301,275,301,314,64,314
            306,276,475,276,475,313,306,313
            65,311,178,311,178,349,65,349
            192,311,310,311,310,348,192,348
            316,313,435,311,435,344,317,347
            69,344,430,344,430,382,69,382
            373,408,447,408,447,435,373,435
            464,408,505,408,505,434,464,434
            522,408,564,408,564,435,522,435
            412,447,600,447,600,489,412,489
            212,448,400,448,400,489,212,489
            """

            text_regions = []
            for region in dummy_text_regions.strip().split("\n"):
                coords = list(map(int, region.split(",")))
                polygon = [coords[i:i+2] for i in range(0, len(coords), 2)]  
                text_regions.append(polygon)

            results.append({
                "id": obj_id,
                "text_regions": text_regions
            })

        return jsonify(results), 200

    except Exception as e:
        app.logger.error(f"Error in predict: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)
