from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from image_processing import crop_and_transform_object, crop_text_regions
import numpy as np
import os
import logging
import json
import base64
import requests
import cv2

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = './static' 
os.makedirs(IMAGE_FOLDER, exist_ok=True) 

logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    app.logger.info("Root endpoint accessed")
    return render_template('file_upload.html')

# 파일 제공 API
@app.route('/static/<filename>', methods=['GET'])
def get_file(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({"message": "File not found"}), 404

# 파일 업로드 API
@app.route('/upload_static', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400
    file = request.files['file']
    file.save(os.path.join(IMAGE_FOLDER, file.filename))
    return jsonify({"message": "File uploaded successfully"}), 200

# 이미지 업로드
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"isSuccess": False, "message": "No file part"}), 404
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"isSuccess": False, "message": "No selected file"}), 404
    
    filename = 'origin.png'
    file_path = os.path.join(IMAGE_FOLDER, filename)
    file.save(file_path)
    
    server_host = "http://backend:5000"  # Docker Compose에서 이 컨테이너의 이름으로 설정
    file_url = f"{server_host}/static/{filename}"
    mmdetection_server_url = 'http://mmdetection:5001/predict'  # Docker Compose 네트워크 이름
    
    try:
        response = requests.post(
            mmdetection_server_url,
            json={"image_path": file_url}
        )
        response.raise_for_status()
        objects_data = response.json()

        # 모든 객체 크롭
        original_image = cv2.imread(file_path)
        if original_image is None:
            return jsonify({"isSuccess": False, "message": "Original image not found"}), 404

        results_dir = os.path.join(IMAGE_FOLDER, 'cropped')
        os.makedirs(results_dir, exist_ok=True)

        for obj in objects_data:
            save_path = crop_and_transform_object(original_image, obj, results_dir)
            file_name = os.path.basename(save_path)
            image_url = f"{server_host}/static/cropped/{file_name}"
            obj["cropped_image_path"] = image_url  # URL 저장

        # CRAFT 요청: type이 "sign"인 객체만
        sign_objects = [obj for obj in objects_data if obj.get("type") == "sign"]
        craft_server_url = 'http://craft:5002/predict'

        if sign_objects:  # sign_objects가 비어 있지 않을 때만 요청
            try:
                craft_response = requests.post(craft_server_url, json=sign_objects)
                craft_response.raise_for_status()

                # 응답이 JSON인지 확인
                if craft_response.headers.get('Content-Type') == 'application/json':
                    craft_results = craft_response.json()

                    # CRAFT 응답 데이터 처리
                    for obj in objects_data:
                        obj["text_regions"] = []
                        for craft_obj in craft_results:
                            if craft_obj["id"] == obj["id"]:
                                # "contains_text" 키가 없는 경우 처리
                                contains_text = craft_obj.get("contains_text", False)
                                obj["contains_text"] = contains_text

                                obj["text_regions"] = [
                                    {"region_id": idx + 1, "polygon": region}
                                    for idx, region in enumerate(craft_obj.get("text_regions", []))
                                ]
                else:
                    app.logger.error("Invalid response format from CRAFT. Expected JSON.")
                    return jsonify({"isSuccess": False, "message": "Invalid response format from CRAFT"}), 500
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Error connecting to CRAFT server: {e}")
                return jsonify({"isSuccess": False, "message": "CRAFT server error"}), 500
            except ValueError as e:
                app.logger.error(f"Error parsing CRAFT response: {e}")
                return jsonify({"isSuccess": False, "message": "Error parsing CRAFT response"}), 500

        # 연속적인 ID 재부여
        for new_id, obj in enumerate(objects_data, start=1):
            obj["id"] = new_id

        # JSON 결과 저장
        objects_json_path = os.path.join(IMAGE_FOLDER, 'objects.json')
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

        # 원본 이미지 Base64 인코딩
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify({
            "isSuccess": True,
            "message": "File uploaded successfully",
            "objects": objects_data,
            "img": encoded_image
        }), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error connecting to MMDetection or CRAFT server: {e}")
        return jsonify({"isSuccess": False, "message": "Detection or CRAFT server error"}), 500
    except Exception as e:
        app.logger.error(f"Error in upload: {e}")
        return jsonify({"isSuccess": False, "message": "Internal Server Error"}), 500

@app.route('/load_result', methods=['POST'])
def load_result():
    try:
        data = request.get_json()
        selected_ids = data.get("selected_ids", [])
        app.logger.info(f"Received IDs: {selected_ids}")

        objects_json_path = os.path.join(IMAGE_FOLDER, 'objects.json')
        with open(objects_json_path, 'r', encoding='utf-8') as json_file:
            objects_data = json.load(json_file)

        # 선택된 객체 필터링
        selected_objects = [obj for obj in objects_data if obj["id"] in selected_ids]

        result_image_path = os.path.join(IMAGE_FOLDER, 'result.png')
        if not os.path.exists(result_image_path):
            return jsonify({"isSuccess": False, "message": "Result image not found"}), 404

        with open(result_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify({
            "isSuccess": True,
            "message": "Success",
            "result": encoded_image,
            "selected_objects": selected_objects
        }), 200
    except Exception as e:
        app.logger.error(f"Error in load_result: {e}")
        return jsonify({"isSuccess": False, "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
