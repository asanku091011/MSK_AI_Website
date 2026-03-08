from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
import os

app = Flask(__name__)

# Load the model
MODEL_PATH = 'keras_model.h5'
LABELS_PATH = 'labels.txt'

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("✓ Model loaded successfully!")

# Load labels
with open(LABELS_PATH, 'r') as f:
    labels = [line.strip().split(' ', 1)[1] for line in f.readlines()]
print(f"✓ Labels loaded: {labels}")

def predict_image(image):
    """Make prediction on uploaded image"""
    # Resize to 224x224 (Teachable Machine standard)
    img = image.convert('RGB')
    img = img.resize((224, 224))
    
    # Convert to array and normalize
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    
    # Get results
    results = []
    for i, label in enumerate(labels):
        results.append({
            'label': label,
            'confidence': float(predictions[0][i] * 100)
        })
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read image
        image = Image.open(io.BytesIO(file.read()))
        
        # Make prediction
        results = predict_image(image)
        
        return jsonify({'predictions': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 Breast Cancer Detection System")
    print("="*60)
    print("\n✓ Server starting...")
    print("✓ Open your browser and go to: http://localhost:5000")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
