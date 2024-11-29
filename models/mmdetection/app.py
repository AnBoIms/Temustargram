from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_path = data.get("image_path")
    if not image_path:
        return jsonify({"error": "No image_path provided"}), 400
    
    # MMDetection 모델 로직 수행 
    # 일단은 신분증일 경우만 넣었어용
    detection_output = """
    1 2,3 4,5 6,7 8
    9 10,11 12,13 14,15 16
    """  # dummy data~

    objects_data = []
    lines = detection_output.strip().split("\n")
    for idx, line in enumerate(lines, start=1):
        coords = [list(map(int, pair.split())) for pair in line.split(",")]
        objects_data.append({
            "id": idx,
            "type": "id_card", 
            "polygon": coords
        })
    return jsonify(objects_data), 200
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)