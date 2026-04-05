from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import tf_keras
import numpy as np
from PIL import Image
import io
import base64
import os
import csv
from datetime import datetime
import uuid

app = Flask(__name__)

# Load the model
MODEL_PATH = 'keras_model.h5'
LABELS_PATH = 'labels.txt'

# CSV Database paths
PATIENTS_DB = 'data/patients.csv'
SCANS_DB = 'data/scans.csv'
HISTORY_DB = 'data/history.csv'

# Initialize databases
def init_databases():
    """Create CSV files if they don't exist"""
    os.makedirs('data', exist_ok=True)
    
    # Patients table
    if not os.path.exists(PATIENTS_DB):
        with open(PATIENTS_DB, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'name', 'date_of_birth', 'gender', 'email', 'phone', 'registration_date'])
    
    # Scans table
    if not os.path.exists(SCANS_DB):
        with open(SCANS_DB, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['scan_id', 'patient_id', 'scan_date', 'result', 'confidence', 'notes'])
    
    # History table (for tracking changes and events)
    if not os.path.exists(HISTORY_DB):
        with open(HISTORY_DB, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['history_id', 'patient_id', 'event_type', 'event_date', 'description'])

print("Initializing databases...")
init_databases()
print("✓ Databases initialized!")

print("Loading model...")
model = tf_keras.models.load_model(MODEL_PATH, compile=False)
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

# Database helper functions
def get_patient_by_id(patient_id):
    """Get patient information by ID"""
    with open(PATIENTS_DB, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['patient_id'] == patient_id:
                return row
    return None

def get_all_patients():
    """Get all patients"""
    patients = []
    with open(PATIENTS_DB, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patients.append(row)
    return patients

def create_patient(name, dob, gender, email, phone):
    """Create a new patient"""
    patient_id = str(uuid.uuid4())[:8]
    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(PATIENTS_DB, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([patient_id, name, dob, gender, email, phone, registration_date])
    
    # Add to history
    add_history(patient_id, 'REGISTRATION', f'Patient {name} registered')
    
    return patient_id

def get_patient_scans(patient_id):
    """Get all scans for a patient"""
    scans = []
    with open(SCANS_DB, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['patient_id'] == patient_id:
                scans.append(row)
    return scans

def add_scan(patient_id, result, confidence, notes=''):
    """Add a new scan result"""
    scan_id = str(uuid.uuid4())[:8]
    scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(SCANS_DB, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([scan_id, patient_id, scan_date, result, confidence, notes])
    
    # Add to history
    add_history(patient_id, 'SCAN', f'New scan: {result} ({confidence}% confidence)')
    
    return scan_id

def get_patient_history(patient_id):
    """Get patient history"""
    history = []
    with open(HISTORY_DB, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['patient_id'] == patient_id:
                history.append(row)
    return history

def add_history(patient_id, event_type, description):
    """Add a history event"""
    history_id = str(uuid.uuid4())[:8]
    event_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(HISTORY_DB, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([history_id, patient_id, event_type, event_date, description])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients"""
    patients = get_all_patients()
    return jsonify({'patients': patients})

@app.route('/api/patient/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details with scans and history"""
    patient = get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    scans = get_patient_scans(patient_id)
    history = get_patient_history(patient_id)
    
    return jsonify({
        'patient': patient,
        'scans': scans,
        'history': history
    })

@app.route('/api/patient/create', methods=['POST'])
def create_new_patient():
    """Create a new patient"""
    data = request.json
    
    required_fields = ['name', 'dob', 'gender', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    patient_id = create_patient(
        data['name'],
        data['dob'],
        data['gender'],
        data['email'],
        data['phone']
    )
    
    return jsonify({
        'success': True,
        'patient_id': patient_id,
        'message': 'Patient registered successfully'
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    if 'patient_id' not in request.form:
        return jsonify({'error': 'No patient ID provided'}), 400
    
    file = request.files['file']
    patient_id = request.form['patient_id']
    notes = request.form.get('notes', '')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Verify patient exists
    patient = get_patient_by_id(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        # Read image
        image = Image.open(io.BytesIO(file.read()))
        
        # Make prediction
        results = predict_image(image)
        
        # Save scan to database
        top_result = results[0]
        scan_id = add_scan(
            patient_id,
            top_result['label'],
            round(top_result['confidence'], 2),
            notes
        )
        
        return jsonify({
            'predictions': results,
            'scan_id': scan_id,
            'message': 'Scan saved successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 Breast Cancer Detection System")
    print("="*60)
    print("\n✓ Server starting...")
    print("✓ Open your browser and go to: http://localhost:5001")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5001)