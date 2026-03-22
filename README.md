# 🏥 Breast Cancer Detection Web Application

A beautiful, professional web interface for breast cancer mammogram analysis using AI with complete patient management system.

## 📋 Features

- 🎨 Beautiful, medical-grade UI design
- 👤 **Patient Management System**
  - Register new patients
  - Select existing patients
  - Track patient history
  - Store scan results
- 🖼️ Drag & drop image upload
- ⚡ Real-time AI predictions
- 📊 Confidence scores with visual progress bars
- 💾 **CSV Database Storage** (persists after app restart)
  - Patients table
  - Scans table
  - History table
- 🔒 100% local - no data leaves your computer
- 📱 Responsive design for all devices

## 🗄️ Database Structure

The app uses 3 CSV files to store all data:

### 1. **patients.csv**
- patient_id
- name
- date_of_birth
- gender
- email
- phone
- registration_date

### 2. **scans.csv**
- scan_id
- patient_id
- scan_date
- result (Normal/Cancer)
- confidence (%)
- notes

### 3. **history.csv**
- history_id
- patient_id
- event_type (REGISTRATION, SCAN)
- event_date
- description

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Model Files

Place these files in the same folder as `app.py`:
- `keras_model.h5` (your trained model)
- `labels.txt` (your class labels)

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## 📁 Project Structure

```
breast-cancer-detection/
├── app.py                 # Flask backend with patient management
├── templates/
│   └── index.html        # Frontend UI with patient forms
├── data/                 # CSV databases (auto-created)
│   ├── patients.csv      # Patient records
│   ├── scans.csv         # Scan results
│   └── history.csv       # Event history
├── keras_model.h5        # Your trained model (add this)
├── labels.txt            # Class labels (add this)
└── requirements.txt      # Python dependencies
```

## 🎯 How to Use

1. **Open the web app** in your browser
2. **Select Patient Type:**
   - **Existing Patient**: Choose from dropdown list
   - **New Patient**: Fill in registration form (name, DOB, gender, email, phone)
3. **View Patient History** (if existing patient with previous scans)
4. **Upload Mammogram Image:**
   - Click the upload area or drag & drop
   - Supports JPG, PNG, PGM formats
5. **Analyze Image:**
   - Click "Analyze Image" button
   - View AI predictions with confidence scores
6. **Add Notes** (optional): Document observations about the scan
7. **Review History:** See all previous scans and results for the patient

## 📊 Patient Workflow

```
New Visit → Select/Register Patient → View History → Upload Scan → 
Analyze → Review Results → Add Notes → Saved to Database
```

All data persists in CSV files, so patient records are available even after restarting the application!

## ⚠️ Important Notes

- This tool is for **educational and research purposes only**
- Not a substitute for professional medical diagnosis
- Always consult qualified healthcare professionals
- All processing is done locally on your machine

## 🛠️ Troubleshooting

**Port already in use?**
```bash
# Change the port in app.py (last line):
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

**Model not loading?**
- Ensure `keras_model.h5` and `labels.txt` are in the same directory as `app.py`
- Check that TensorFlow is properly installed

**Image upload not working?**
- Supported formats: JPG, PNG, PGM
- Maximum file size: 10MB

## 📊 Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- PGM (.pgm)
- Other standard image formats

## 🎨 UI Design

The interface features:
- Clean, professional medical aesthetic
- Smooth animations and transitions
- Responsive layout for mobile and desktop
- Accessibility-friendly design
- High contrast for easy reading

## 🔧 Customization

You can customize the colors in `templates/index.html` by changing the CSS variables:

```css
:root {
    --primary: #2D5F5D;        /* Main brand color */
    --secondary: #E8927C;       /* Accent color */
    --background: #F8F6F3;      /* Page background */
    /* ... more variables ... */
}
```

## 📝 License

This project is for educational purposes. Please ensure compliance with medical data regulations in your jurisdiction.

## 🙏 Acknowledgments

- Model trained on MIAS Mammography Database
- Built with Flask and TensorFlow
- UI design inspired by modern medical applications