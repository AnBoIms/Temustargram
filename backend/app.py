from flask import Flask, request, jsonify, render_template
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
    
    server_host = request.host_url.strip("/") 
    file_url = f"{server_host}/static/{filename}" 
    
    mmdetection_server_url = 'http://localhost:5001/predict'  
    #docker-compose로 돌릴땐 아래 코드
    # mmdetection_server_url = 'http://mmdetection:5001/predict'  
    try:
        response = requests.post(
            mmdetection_server_url,
            json={"image_path": file_url} 
        )
        response.raise_for_status() 
        objects_data = response.json()
        with open(os.path.join(IMAGE_FOLDER, 'objects.json'), 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return jsonify({
            "isSuccess": True,
            "message": "File uploaded successfully",
            "objects": objects_data,
            "img": encoded_image
        }), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error connecting to MMDetection server: {e}")
        return jsonify({
            "isSuccess": False,
            "message": "Error connecting to detection server"
        }), 500

@app.route('/load_result', methods=['POST'])
def load_result():
    try:
        data = request.get_json()
        selected_ids = data.get("selected_ids", [])
        app.logger.info(f"Received IDs: {selected_ids}")

        objects_json_path = os.path.join(IMAGE_FOLDER, 'objects.json')
        with open(objects_json_path, 'r', encoding='utf-8') as json_file:
            objects_data = json.load(json_file)

        original_image_path = os.path.join(IMAGE_FOLDER, 'origin.png')
        img = cv2.imread(original_image_path)
        if img is None:
            return jsonify({"isSuccess": False, "message": "Original image not found"}), 404
        
        results_dir = os.path.join(IMAGE_FOLDER, 'cropped')
        os.makedirs(results_dir, exist_ok=True)
        
        server_host = request.host_url.strip("/")  
        cropped_images = [] 
        selected_objects = []
        for obj in objects_data:
            if obj["id"] in selected_ids:
                save_path = crop_and_transform_object(img, obj, results_dir)
                file_name = os.path.basename(save_path)
                image_url = f"{server_host}/static/cropped/{file_name}"
                cropped_images.append(image_url)
                
                obj["cropped_image_path"] = image_url
                selected_objects.append(obj)
        
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

        # craft로 보냄
        craft_server_url = 'http://localhost:5002/predict' 
        # craft_server_url = 'http://craft:5002/predict' 
        response = requests.post(craft_server_url, json=selected_objects)
        response.raise_for_status()
        craft_response = response.json() 

        # CRAFT 응답 데이터를 객체에 추가
        for obj in selected_objects:
            for craft_obj in craft_response:
                if craft_obj["id"] == obj["id"]:
                    obj["text_regions"] = []
                    for i, region in enumerate(craft_obj["text_regions"], start=1):
                        polygon = [point for point in region]  
                        obj["text_regions"].append({
                            "region_id": i,
                            "polygon": polygon 
                        })
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

        text_results_dir = os.path.join(IMAGE_FOLDER, 'text_regions')
        crop_text_regions(selected_objects, text_results_dir, server_host)
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

        result_image_path = os.path.join(IMAGE_FOLDER, 'result.png')

        # 자른 이미지 path를 SRNet으로 넘김
        # 변환된 text 이미지 파일을 원본 text 이미지 파일과 같은 directory에 다른 이름으로 저장
        # OD 이미지에 좌표대로 합성
        # 원본 이미지에 OD 이미지 합성 후 result.png로 저장

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
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)