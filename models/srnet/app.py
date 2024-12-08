from flask import Flask, request, jsonify
from i_t_creator import process_all_images
from predict import run_srnet
import torch
import os
import logging

app = Flask(__name__)

input_folder = os.getenv("INPUT_FOLDER", "/srnet/static/text_regions")
label_output_folder = os.getenv("LABEL_OUTPUT_FOLDER", "/srnet/labels/")
font_path = os.getenv("FONT_PATH", "/srnet/hangil.ttf")
results_folder = input_folder

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])
def process_images():
    try:
        # Step 1: Process images (gray background with text)
        file_mapping = process_all_images(input_folder, label_output_folder, "안보임스", font_path)

        # Step 2: Run SRNet for prediction
        run_srnet(
            input_dir=label_output_folder,
            save_dir=results_folder,
            checkpoint_path="trained_final_5M_.model", 
            learning_rate=0.0002,
            beta1=0.5,
            beta2=0.999,
            file_mapping=file_mapping,
            device=device
        )

        return jsonify({"status": "success", "message": "Prediction completed"}), 200

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
