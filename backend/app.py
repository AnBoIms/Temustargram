from flask import Flask, request, jsonify, render_template
import os
import logging
import json

app = Flask(__name__)
UPLOAD_FOLDER = './static' 
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world():
    app.logger.info("Root endpoint accessed")
    return render_template('file_upload.html')

# 이미지 업로드
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"isSuccess": False, "message": "No file part"}),400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"isSuccess": False, "message": "No selected file"}),400
    
    filename = 'origin.png'
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    #여기에 mmdetection, return 결과 json에 추가

    objects_data = [{
        "id": 1,
        "type": "id_card",
        "polygon": [[901, 2091], [1156, 1687], [1800, 2095], [1546, 2498]]
    }] #뒤에 더 객체들 추가
    with open(os.path.join(UPLOAD_FOLDER, 'objects.json'), 'w', encoding='utf-8') as json_file:
        json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

    return jsonify({
        "isSuccess": True,
        "message": "File uploaded successfully",
        "objects":objects_data
    }),200

@app.route('/load_result', methods=['POST'])
def load_result():
    return

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