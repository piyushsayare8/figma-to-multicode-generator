# Model Integration Guide

## Using Your Trained Model in the Project

This guide explains how to integrate your trained `ui_classification_model.h5` into the Figma to Multicode Generator.

---

## Quick Setup

### 1. Place Your Model File

Copy your trained model to the models directory:

```bash
# From the project root
cp ui_classification_model.h5 backend/models/
```

Or manually place it at:
```
backend/models/ui_classification_model.h5
```

### 2. Install TensorFlow

The backend now requires TensorFlow:

```bash
cd backend
pip install tensorflow>=2.13.0
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the Backend

```bash
# Option 1: Using PowerShell script (Windows)
.\run_backend.ps1

# Option 2: Manual activation
.\.venv\Scripts\Activate.ps1
uvicorn app_new:app --reload --host 0.0.0.0 --port 8000
```

---

## How It Works

### Model Integration Architecture

```
User Upload
    ↓
[FastAPI Endpoint]
    ↓
[OpenCV Detection] → Detects UI blocks (bounding boxes)
    ↓
[TensorFlow Classifier] → Your trained model classifies each block
    ↓
[ILS Builder] → Creates Intermediate Layout Schema
    ↓
[Code Generators] → Generates HTML/React/Flutter code
    ↓
Response to User
```

### File Structure

```
backend/
├── models/
│   ├── ui_classification_model.h5  ← Your trained model goes here
│   └── README.md
├── utils/
│   ├── detection.py               ← OpenCV block detection
│   ├── tf_classifier.py          ← TensorFlow model integration (NEW)
│   ├── ils_builder.py            ← Layout schema builder
│   ├── style_analyzer.py         ← Style extraction
│   ├── generator_html_css_enhanced.py
│   ├── generator_tailwind_enhanced.py
│   ├── generator_react_enhanced.py
│   └── generator_flutter_enhanced.py
├── app_new.py                     ← Main FastAPI app
└── requirements.txt               ← Updated with TensorFlow
```

---

## Model Specifications

Your model must meet these requirements:

### Input Format
- **Shape:** `(None, 224, 224, 3)`
- **Data Type:** Float32
- **Normalization:** Values in range [0, 1]
- **Color Space:** RGB

### Output Format
- **Shape:** `(None, 9)` - 9 classes
- **Classes (in order):**
  1. background
  2. button
  3. card
  4. heading
  5. image_block
  6. input_field
  7. link
  8. password_input
  9. text_block

### Class Mapping

The classifier automatically maps model predictions to UI element types:

| Model Class      | UI Element Type |
|-----------------|-----------------|
| background      | container       |
| button          | button          |
| card            | card            |
| heading         | heading         |
| image_block     | image           |
| input_field     | text_input      |
| link            | link            |
| password_input  | text_input      |
| text_block      | text            |

---

## Testing Your Integration

### 1. Check Model Loading

Start the backend and look for this log message:

```
INFO: Loading trained model from: backend/models/ui_classification_model.h5
INFO: ✓ Model loaded successfully from backend/models/ui_classification_model.h5
```

### 2. Test with API

Upload a test image:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@test_ui_screenshot.png"
```

### 3. Check Classification Results

The response should include:

```json
{
  "layout": [
    {
      "x": 100,
      "y": 50,
      "w": 200,
      "h": 40,
      "type": "button",
      "confidence": 0.95
    }
  ],
  "ils": {...},
  "outputs": {...}
}
```

---

## Troubleshooting

### Model Not Found

**Symptom:**
```
WARNING: Model file not found at: backend/models/ui_classification_model.h5
WARNING: Will use fallback geometric classifier
```

**Solution:**
- Ensure the model file is in the correct location
- Check file name spelling: `ui_classification_model.h5`
- Verify file permissions

### TensorFlow Import Error

**Symptom:**
```
WARNING: TensorFlow not available - using fallback classifier
```

**Solution:**
```bash
pip install tensorflow>=2.13.0
```

### Low Prediction Confidence

**Symptom:**
```
DEBUG: Low confidence (0.35) for prediction, using fallback
```

**Possible Causes:**
- Model needs more training
- Input image quality is poor
- UI element not in training dataset

**Solution:**
- Retrain model with more diverse data
- Adjust confidence threshold in `tf_classifier.py`

### Memory Issues

**Symptom:**
```
ERROR: OOM when allocating tensor
```

**Solution:**
- Reduce batch size (currently processes one at a time)
- Use TensorFlow Lite for smaller memory footprint
- Increase system memory

---

## Advanced Configuration

### Custom Model Path

Set environment variable:

```bash
export MODEL_PATH="/path/to/custom/model.h5"
```

Or modify `config.py`:

```python
MODEL_PATH = Path("/path/to/custom/model.h5")
```

### Adjust Confidence Threshold

Edit `backend/utils/tf_classifier.py`:

```python
CONFIDENCE_THRESHOLD = 0.5  # Change this value (0.0 to 1.0)
```

### Different Model Architecture

If your model uses different input size or classes, update:

```python
# In tf_classifier.py
MODEL_INPUT_SIZE = 224  # Change to your size
CLASS_NAMES = [...]      # Update class names
```

---

## Performance Optimization

### GPU Acceleration

TensorFlow automatically uses GPU if available:

```bash
# Install GPU support
pip install tensorflow[and-cuda]
```

### Model Optimization

Convert to TensorFlow Lite for faster inference:

```python
import tensorflow as tf

# Convert model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save
with open('ui_model.tflite', 'wb') as f:
    f.write(tflite_model)
```

Then update the classifier to use TFLite interpreter.

---

## Integration Checklist

- [ ] Trained model file copied to `backend/models/ui_classification_model.h5`
- [ ] TensorFlow installed (`pip install tensorflow`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend starts without errors
- [ ] Model loads successfully (check logs)
- [ ] Test API endpoint with sample image
- [ ] Classification results look reasonable
- [ ] Frontend can connect and display results

---

## Next Steps

Once your model is integrated:

1. **Test with Real Data:** Upload various UI screenshots
2. **Monitor Performance:** Check accuracy and speed
3. **Collect Feedback:** Gather user feedback on classification quality
4. **Iterate:** Retrain model with edge cases
5. **Deploy:** Move to production environment

---

## Support

If you encounter issues:

1. Check the logs in the terminal
2. Review the troubleshooting section
3. Verify model file integrity
4. Test with simple UI screenshots first
5. Gradually increase complexity

The system includes fallback mechanisms, so it will continue to work even if the model fails to load, though with reduced accuracy.
