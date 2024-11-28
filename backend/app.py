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
    return render_template('file_upload.html')

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
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return jsonify({
        "isSuccess": True,
        "message": "File uploaded successfully",
        "objects": objects_data,
        "img": encoded_image  # Base64 인코딩된 이미지
    }), 200


@app.route('/load_result', methods=['POST'])
def load_result():
    try:
        data = request.get_json()
        selected_ids = data.get("selected_ids", [])
        
        app.logger.info(f"Received IDs: {selected_ids}")

        # 선택한 id에 한해서 이미지 crop하여 저장
        # 만약 type이 id_card이면 crop 후 선형변환해서 저장(static에 id별로 directory 나눠서).
        # crop한 이미지들의 img_path를 json에 추가
        # Craft에 img_path를 넘김(docker-compose-volumn에 공유폴더로)
        # response로 text detection된 좌표 response로 받고, 좌표대로 하위 directory에 잘라서 저장
        # 이때 detection된 좌표들 및 image_path json 하위 그룹에 text_regions으로 저장
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