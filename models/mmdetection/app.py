from mmdet.apis import init_detector, inference_detector
from flask import Flask, request, jsonify
from flask_cors import CORS
from idcard_output import get_coordinate
from shapely.geometry import Polygon
import numpy as np
import logging
import requests
import os
import shutil

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = './downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

id_config_file = 'configs/anboims_dataset/id_mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset.py'
sign_config_file = 'configs/anboims_dataset/sign_mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset.py'
id_checkpoint_file = 'work_dirs/id_epoch_24.pth'
sign_checkpoint_file = 'work_dirs/sign_epoch_24.pth'
id_model = init_detector(id_config_file, id_checkpoint_file, device='cpu')
sign_model = init_detector(sign_config_file, sign_checkpoint_file, device='cpu')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_path = data.get("image_path")
    if not image_path:
        return jsonify({"error": "No image_path provided"}), 400

    try:
        response = requests.get(image_path, stream=True)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 400
        
        file_name = os.path.basename(image_path)
        local_image_path = os.path.join(DOWNLOAD_FOLDER, file_name)

        with open(local_image_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        app.logger.info(f"Image downloaded and saved as {local_image_path}")
    except Exception as e:
        app.logger.error(f"Error downloading image: {e}")
        return jsonify({"error": "Error downloading image"}), 500

    # ID 모델 추론
    id_result = inference_detector(id_model, local_image_path)
    id_masks = id_result.pred_instances.masks.cpu().numpy()
    id_convex_coordinates = []

    for mask in id_masks:
        if mask.sum() > 0:
            segmentation_points = np.argwhere(mask > 0)
            segmentation_points = [(x, y) for y, x in segmentation_points]
            hull_points = get_coordinate(segmentation_points)
            id_convex_coordinates.append(hull_points)

    # Sign 모델 추론
    sign_result = inference_detector(sign_model, local_image_path)
    sign_masks = sign_result.pred_instances.masks.cpu().numpy()
    sign_convex_coordinates = []

    for mask in sign_masks:
        if mask.sum() > 0:
            segmentation_points = np.argwhere(mask > 0)
            segmentation_points = [(x, y) for y, x in segmentation_points]
            hull_points = get_coordinate(segmentation_points)
            sign_convex_coordinates.append(hull_points)

    objects_data = []

    for idx, coords in enumerate(id_convex_coordinates, start=1):
        objects_data.append({
            "id": idx,
            "type": "id_card",
            "polygon": coords
        })

    id_polygons = [Polygon(coords) for coords in id_convex_coordinates]

    filtered_sign_coordinates = []

    for coords in sign_convex_coordinates:
        sign_polygon = Polygon(coords)
        overlap = False

        # ID Card와 겹치는지 확인
        for id_polygon in id_polygons:
            if sign_polygon.intersects(id_polygon): 
                overlap = True
                break

        if not overlap: 
            filtered_sign_coordinates.append(coords)

    for idx, coords in enumerate(filtered_sign_coordinates, start=len(id_convex_coordinates) + 1):
        objects_data.append({
            "id": idx,
            "type": "sign",
            "polygon": coords
        })

    response_data = jsonify(objects_data)

    try:
        os.remove(local_image_path)
        app.logger.info(f"Image file {local_image_path} deleted after response")
    except Exception as e:
        app.logger.error(f"Error deleting image file: {e}")

    return response_data, 200

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)