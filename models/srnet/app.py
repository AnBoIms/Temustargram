from flask import Flask, request, jsonify
import os
import requests
import shutil
import subprocess
import logging

app = Flask(__name__)

# 다운로드 및 출력 폴더 설정
DOWNLOAD_FOLDER = './downloads'
OUTPUT_FOLDER = './static/processed'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])
def process_images():
    try:
        # 클라이언트로부터 이미지 URL 리스트 받기
        data = request.get_json()
        image_urls = data.get("image_urls")
        if not image_urls:
            return jsonify({"error": "No image URLs provided"}), 400

        downloaded_files = []
        for image_url in image_urls:
            file_name = os.path.basename(image_url)
            local_path = os.path.join(DOWNLOAD_FOLDER, file_name)

            # 이미지 다운로드
            response = requests.get(image_url, stream=True)
            if response.status_code != 200:
                return jsonify({"error": f"Failed to download {image_url}"}), 400

            with open(local_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

            downloaded_files.append(local_path)

        # SRNet `predict.py` 실행
        subprocess.run([
            "python3", "predict.py",
            "--input_dir", DOWNLOAD_FOLDER,
            "--save_dir", OUTPUT_FOLDER,
            "--checkpoint", "logs/trained_final_5M_.model"
        ], check=True)

        # 결과 파일 경로 생성
        processed_files = [
            f"/static/processed/{os.path.basename(f)}"
            for f in os.listdir(OUTPUT_FOLDER)
            if f.endswith("o_f.png")
        ]

        return jsonify({"processed_files": processed_files}), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"SRNet execution failed: {e}")
        return jsonify({"error": f"SRNet execution failed: {e}"}), 500
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
