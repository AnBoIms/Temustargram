from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import json
import base64

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = './static' 
os.makedirs(IMAGE_FOLDER, exist_ok=True) 

logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    app.logger.info("Root endpoint accessed")
    return render_template('load_img.html')

# 이미지 업로드
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"isSuccess": False, "message": "No file part"}),404
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"isSuccess": False, "message": "No selected file"}),404
    
    filename = 'origin.png'
    file_path = os.path.join(IMAGE_FOLDER, filename)
    file.save(file_path)
    
    #여기에 mmdetection, return 결과 json에 추가

    objects_data = [{
        "id": 1,
        "type": "id_card",
        "polygon": [[901, 2091], [1156, 1687], [1800, 2095], [1546, 2498]]
    }] #example
    with open(os.path.join(IMAGE_FOLDER, 'objects.json'), 'w', encoding='utf-8') as json_file:
        json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

    return jsonify({
        "isSuccess": True,
        "message": "File uploaded successfully",
        "objects":objects_data
    }),200

@app.route('/load_result', methods=['POST'])
def load_result():
    try:
        data = request.get_json()
        selected_ids = data.get("selected_ids", [])
        
        app.logger.info(f"Received IDs: {selected_ids}")

        # 중간 처리 부분 (선형 변환, CRAFT, SRNet 등)은 여기에 추가

        result_image_path = os.path.join(IMAGE_FOLDER, 'result.png')
        
        if not os.path.exists(result_image_path):
            return jsonify({
                "isSuccess": False,
                "message": "Result image not found"
            }), 404
        
        with open(result_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        return jsonify({
            "isSuccess": True,
            "message": "success",
            "result": encoded_image 
        }), 200

    except Exception as e:
        app.logger.error(f"Error in load_result: {e}")
        return jsonify({
            "isSuccess": False,
            "message": "Internal Server Error"
        }), 500

#error 처리
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    return jsonify({
        "isSuccess": False,
        "message": "Internal Server Error",
    }),500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)