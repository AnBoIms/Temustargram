from image_processing import crop_and_transform_object, insert_image_final, crop_text_regions, merge_text_regions
from idcard_processor import ocr_result, process_ocr_results, process_bounding_box, apply_blur
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging
import base64
import shutil
import json
import os
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

    mmdetection_server_url = 'http://mmdetection:5001/predict'

    try:
        # MMDetection server request
        response = requests.post(mmdetection_server_url)
        response.raise_for_status()
        objects_data = response.json()

        original_image = cv2.imread(file_path)
        if original_image is None:
            app.logger.error("Original image not found or unreadable")
            return jsonify({"isSuccess": False, "message": "Original image not found"}), 404

        results_dir = os.path.join(IMAGE_FOLDER, 'cropped')
        os.makedirs(results_dir, exist_ok=True)

        # crop object
        for obj in objects_data:
            save_path, new_polygon = crop_and_transform_object(original_image, obj, results_dir)
            file_name = os.path.basename(save_path)
            relative_path = save_path.replace('./static/', '')
            obj["cropped_image_path"] = f"/static/{relative_path}"
            obj["polygon"] = new_polygon.tolist()

        # CRAFT server request
        sign_objects = [obj for obj in objects_data if obj.get("type") == "sign"]
        if sign_objects:
            craft_server_url = 'http://craft:5002/predict'
            craft_response = requests.post(craft_server_url, json=sign_objects)
            craft_response.raise_for_status()

            if craft_response.headers.get('Content-Type') == 'application/json':
                craft_results = craft_response.json()
                for obj in objects_data:
                    obj["text_regions"] = []
                    for craft_obj in craft_results:
                        if craft_obj["id"] == obj["id"]:
                            obj["contains_text"] = craft_obj.get("contains_text", False)
                            obj["text_regions"] = [
                                {"region_id": idx + 1, "polygon": region}
                                for idx, region in enumerate(craft_obj.get("text_regions", []))
                            ]

            else:
                app.logger.error("Invalid response format from CRAFT.")
                return jsonify({"isSuccess": False, "message": "Invalid response format from CRAFT"}), 500

        objects_json_path = os.path.join(IMAGE_FOLDER, 'objects.json')
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(objects_data, json_file, ensure_ascii=False, indent=4)

        # Base64 encoding
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify({
            "isSuccess": True,
            "message": "File uploaded successfully",
            "objects": objects_data,
            "img": encoded_image
        }), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error connecting to detection servers: {e}")
        return jsonify({"isSuccess": False, "message": "Detection server error"}), 500
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

        selected_objects = [obj for obj in objects_data if obj["id"] in selected_ids]
        unselected_objects = [obj for obj in objects_data if obj["id"] not in selected_ids]

        for obj in unselected_objects:
            cropped_image_path = obj["cropped_image_path"].replace("/static/", "./static/")
            cropped_image_path = os.path.abspath(cropped_image_path)
            if os.path.exists(cropped_image_path):
                os.remove(cropped_image_path)
                app.logger.info(f"Deleted cropped image: {cropped_image_path}")
            else:
                app.logger.warning(f"Cropped image not found: {cropped_image_path}")

        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(selected_objects, json_file, ensure_ascii=False, indent=4)
            app.logger.info("Updated objects.json with selected objects")

        # EasyOCR image processing(id_card)
        for obj in selected_objects:
            if obj["type"] == "id_card":
                cropped_image_path = obj["cropped_image_path"].replace("/static/", "./static/")
                cropped_image_path = os.path.abspath(cropped_image_path)
                textures = {
                    "name": 'text_image/name.png',
                    "resident_id": 'text_image/number.png',
                    "address": 'text_image/address.png'
                }

                # OCR process
                ocr_results = ocr_result(cropped_image_path)
                processed_results = process_ocr_results(ocr_results)
                image = cv2.imread(cropped_image_path)
                
                if not processed_results or not processed_results["name"] or not processed_results["resident_id"] or not processed_results["address"]:
                    success = apply_blur(cropped_image_path, cropped_image_path)
                    if success:
                        app.logger.info(f"Blur process completed for {cropped_image_path}")
                    else:
                        app.logger.error(f"Blur process failed for {cropped_image_path}")
                else:
                    for category, bounding_box_data in processed_results.items():
                        if bounding_box_data and isinstance(bounding_box_data, list):
                            for bounding_box, _ in bounding_box_data:
                                texture_path = textures.get(category)
                                if texture_path:
                                    image = process_bounding_box(image, texture_path, bounding_box)
                    cv2.imwrite(cropped_image_path, image)
                    app.logger.info(f"OCR processed and saved: {cropped_image_path}")

        # crop text image
        text_regions_dir = os.path.join(IMAGE_FOLDER, 'text_regions')
        selected_objects = crop_text_regions(selected_objects, text_regions_dir)
        app.logger.info("Text image regions cropped!")

        app.logger.info(f"Updated selected_objects: {selected_objects}")

        objects_json_path = os.path.join(IMAGE_FOLDER, 'objects.json')
        with open(objects_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(selected_objects, json_file, ensure_ascii=False, indent=4)
            app.logger.info("Updated objects.json with cropped text regions.")

        # SRNet image processing(Sign)
        has_sign_objects = any(obj["type"] == "sign" for obj in selected_objects)
        if has_sign_objects:
            srnet_server_url = "http://srnet:5003/predict" 
            try:
                srnet_response = requests.post(srnet_server_url)
                srnet_response.raise_for_status()
                if srnet_response.status_code == 200:
                    app.logger.info("SRNet processing completed successfully.")
                else:
                    app.logger.error(f"SRNet returned an error: {srnet_response.status_code}")
                    return jsonify({"isSuccess": False, "message": "SRNet processing failed"}), 500
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Error connecting to SRNet server: {e}")
                return jsonify({"isSuccess": False, "message": "SRNet server error"}), 500

        # text region synthesis
        for obj in selected_objects:
            if obj["type"] == "sign":
                success = merge_text_regions(obj)
                if success:
                    app.logger.info(f"Merged text regions for {obj['cropped_image_path']}")
                else:
                    app.logger.error(f"Failed to merge text regions for {obj['cropped_image_path']}")

        # final synthesis
        original_image_path = os.path.join(IMAGE_FOLDER, 'origin.png')
        original_image = cv2.imread(original_image_path)
        if original_image is None:
            return jsonify({"isSuccess": False, "message": "Original image not found"}), 404

        temp_image_path = os.path.join(IMAGE_FOLDER, 'temp_result.png')
        cv2.imwrite(temp_image_path, original_image)

        for obj in selected_objects:
            cropped_image_path = obj["cropped_image_path"].replace("/static/", "./static/")
            cropped_image_path = os.path.abspath(cropped_image_path)
            if os.path.exists(cropped_image_path):
                new_image = cv2.imread(cropped_image_path)
                if new_image is not None:
                    original_image = cv2.imread(temp_image_path)
                    updated_image = insert_image_final(original_image, new_image, obj["polygon"])
                    cv2.imwrite(temp_image_path, updated_image)

        # save final result
        result_image_path = os.path.join(IMAGE_FOLDER, 'result.png')
        cv2.imwrite(result_image_path, updated_image)
        app.logger.info(f"Final result saved: {result_image_path}")

        with open(result_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return jsonify({
            "isSuccess": True,
            "message": "Success",
            "result": encoded_image
        }), 200
    except Exception as e:
        app.logger.error(f"Error in load_result: {e}")
        return jsonify({"isSuccess": False, "message": "Internal Server Error"}), 500

@app.after_request
def after_request(response):
    if request.endpoint == 'load_result':
        for filename in os.listdir(IMAGE_FOLDER):
            file_path = os.path.join(IMAGE_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) 
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) 
            except Exception as e:
                app.logger.error(f"Error deleting {file_path}: {e}")
    app.logger.info(f"images Deleted")
    return response

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
