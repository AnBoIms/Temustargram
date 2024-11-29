from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import json

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

@app.route('/predict', methods=['POST'])
def predict():
    return
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5003, debug=True)