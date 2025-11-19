# Quick Start: Using Your Trained Model

Follow these simple steps to integrate your trained `ui_classification_model.h5` into the project.

## 1. Place Your Model File (30 seconds)

Copy your trained model to the backend models directory:

```bash
# From your project root
cp ui_classification_model.h5 backend/models/
```

Expected location:
```
backend/models/ui_classification_model.h5
```

## 2. Install Dependencies (2-3 minutes)

```bash
cd backend

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# OR
source .venv/bin/activate    # Linux/Mac

# Install TensorFlow and dependencies
pip install tensorflow>=2.13.0
pip install -r requirements.txt
```

## 3. Start the Backend (10 seconds)

### Option A: Using PowerShell Script (Easiest - Windows)
```bash
.\run_backend.ps1
```

### Option B: Manual Start
```bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn app_new:app --reload --host 0.0.0.0 --port 8000
```

## 4. Verify Model Loading

Look for these messages in the terminal:

✅ **Success:**
```
INFO: Loading trained model from: backend/models/ui_classification_model.h5
INFO: ✓ Model loaded successfully from backend/models/ui_classification_model.h5
INFO: Application startup complete.
```

⚠️ **Warning (model not found):**
```
WARNING: Model file not found at: backend/models/ui_classification_model.h5
WARNING: Will use fallback geometric classifier
```

## 5. Start the Frontend (30 seconds)

```bash
cd frontend
npm install  # First time only
npm run dev
```

## 6. Test the System

1. Open browser: `http://localhost:5173`
2. Upload a UI screenshot
3. Click "Generate Code"
4. Check the results!

## Verification Checklist

- [ ] Model file is in `backend/models/ui_classification_model.h5`
- [ ] Backend starts without errors
- [ ] Log shows "Model loaded successfully"
- [ ] Frontend is accessible at `http://localhost:5173`
- [ ] Can upload and analyze images
- [ ] Classification results appear reasonable

## Quick Test

Use this curl command to test the API:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@your_ui_screenshot.png"
```

Expected response includes:
```json
{
  "layout": [
    {
      "type": "button",
      "confidence": 0.95,
      ...
    }
  ]
}
```

## Troubleshooting

### Model Not Loading

**Problem:** Model file not found
**Fix:** 
```bash
# Verify file exists
ls backend/models/ui_classification_model.h5

# Check file size (should be several MB)
ls -lh backend/models/ui_classification_model.h5
```

### TensorFlow Not Installed

**Problem:** `ModuleNotFoundError: No module named 'tensorflow'`
**Fix:**
```bash
pip install tensorflow>=2.13.0
```

### Port Already in Use

**Problem:** `Error: Address already in use`
**Fix:**
```bash
# Use different port
uvicorn app_new:app --reload --host 0.0.0.0 --port 8001
```

Then update `frontend/src/config.js`:
```javascript
export const API_BASE_URL = "http://localhost:8001";
```

## What's Next?

- 📖 Read [MODEL_INTEGRATION.md](backend/MODEL_INTEGRATION.md) for advanced configuration
- 🎯 Test with various UI screenshots
- 🔧 Adjust confidence threshold if needed
- 📊 Monitor classification accuracy
- 🔄 Retrain model with more data if needed

## Support

If something doesn't work:

1. Check all logs in the terminal
2. Verify Python version: `python --version` (needs 3.8+)
3. Verify TensorFlow installation: `python -c "import tensorflow; print(tensorflow.__version__)"`
4. Check model file integrity
5. Try with a simple, clear UI screenshot first

---

**Estimated Total Setup Time: 5 minutes**

The system will work even without the model (using fallback classifier), but accuracy will be significantly better with your trained model!
