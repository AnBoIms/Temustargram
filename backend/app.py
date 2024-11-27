from flask import Flask, request, jsonify, render_template
import os
import logging

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
    
    return jsonify({
        "isSuccess": True,
        "message": "File uploaded successfully",
        "objects":[]
    }),200

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
