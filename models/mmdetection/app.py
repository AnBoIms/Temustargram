from mmdet.apis import init_detector, inference_detector
from flask import Flask, jsonify
from flask_cors import CORS
from idcard_output import get_coordinate
from shapely.geometry import Polygon
import numpy as np
import logging
import os

app = Flask(__name__)
CORS(app)

STATIC_FOLDER = os.getenv("STATIC_FOLDER", "/mmdetection/static")  
IMAGE_FILENAME = "origin.png"
IMAGE_PATH = os.path.join(STATIC_FOLDER, IMAGE_FILENAME)

logging.basicConfig(level=logging.INFO)

# model initialize
id_config_file = "configs/anboims_dataset/id_mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset.py"
sign_config_file = "configs/anboims_dataset/sign_mask-rcnn_r50-caffe_fpn_ms-poly-1x_anboimsdataset.py"
id_checkpoint_file = "work_dirs/id_epoch_24.pth"
sign_checkpoint_file = "work_dirs/sign_epoch_24.pth"
id_model = init_detector(id_config_file, id_checkpoint_file, device="cpu")
sign_model = init_detector(sign_config_file, sign_checkpoint_file, device="cpu")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        app.logger.info(f"Checking for image at {IMAGE_PATH}")
        if not os.path.exists(IMAGE_PATH):
            app.logger.error(f"Image file {IMAGE_FILENAME} not found in static folder.")
            return jsonify({"error": "Image file not found in static folder"}), 400

        app.logger.info(f"Using image {IMAGE_FILENAME} from static folder")

        # ID model predict
        id_result = inference_detector(id_model, IMAGE_PATH)
        id_masks = id_result.pred_instances.masks.cpu().numpy()
        id_convex_coordinates = []

        for mask in id_masks:
            if mask.sum() > 0:
                segmentation_points = np.argwhere(mask > 0)
                segmentation_points = [(x, y) for y, x in segmentation_points]
                hull_points = get_coordinate(segmentation_points)
                id_convex_coordinates.append(hull_points)

        # Sign model predict
        sign_result = inference_detector(sign_model, IMAGE_PATH)
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

        app.logger.info(f"Prediction completed with {len(objects_data)} objects detected.")
        return jsonify(objects_data), 200

    except Exception as e:
        app.logger.error(f"Error during prediction: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
