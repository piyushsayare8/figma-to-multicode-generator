# Project Verification Checklist

Run through this checklist to ensure your project is ready to run.

## ✅ Pre-Flight Checklist

### 1. Model File Placement
- [ ] Model file exists at `backend/models/ui_classification_model.h5`
- [ ] Model file size is reasonable (should be several MB)
- [ ] Model file is not corrupted

**Verify:**
```bash
ls -lh backend/models/ui_classification_model.h5
```

### 2. Backend Dependencies
- [ ] Python 3.8+ is installed
- [ ] Virtual environment is created
- [ ] All dependencies are installed including TensorFlow

**Verify:**
```bash
cd backend
python --version
.venv\Scripts\python -c "import tensorflow; print(f'TensorFlow version: {tensorflow.__version__}')"
.venv\Scripts\python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
.venv\Scripts\python -c "import fastapi; print('FastAPI: OK')"
```

### 3. Frontend Dependencies
- [ ] Node.js 16+ is installed
- [ ] npm packages are installed

**Verify:**
```bash
cd frontend
node --version
npm --version
ls node_modules
```

### 4. Configuration Files
- [ ] `backend/config.py` exists
- [ ] `frontend/src/config.js` points to correct backend URL
- [ ] CORS is properly configured

**Verify:**
```bash
# Check backend config
cat backend/config.py | grep MODEL_PATH

# Check frontend config
cat frontend/src/config.js | grep API_BASE_URL
```

## 🚀 Launch Sequence

### Option 1: Quick Start (Windows)
```bash
.\go.bat
```
This will:
1. Start backend on port 8000
2. Start frontend on port 5173
3. Open browser automatically

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn app_new:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🔍 Verification Steps

### Step 1: Check Backend Health
Open browser or use curl:
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**If `model_loaded` is `false`:**
- Model file is missing or in wrong location
- Check backend logs for error messages
- System will use fallback classifier (reduced accuracy)

### Step 2: Check Backend Logs

Look for these success messages:
```
INFO: Loading trained model from: backend/models/ui_classification_model.h5
INFO: ✓ Model loaded successfully from backend/models/ui_classification_model.h5
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Warning messages to watch for:**
```
WARNING: Model file not found at: backend/models/ui_classification_model.h5
WARNING: Will use fallback geometric classifier
```

### Step 3: Check Frontend

1. Open `http://localhost:5173`
2. You should see the modern dark UI
3. No console errors in browser DevTools

### Step 4: Test Upload

1. Prepare a simple UI screenshot (e.g., a login page)
2. Drag and drop or click to upload
3. Click "Generate Code"
4. Verify you get results

**Expected behavior:**
- Progress bar appears
- Processing takes 1-3 seconds
- Code appears in tabs
- No errors in console

### Step 5: Check API Response

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@test_screenshot.png"
```

**Expected Response Structure:**
```json
{
  "layout": [
    {
      "x": 100,
      "y": 50,
      "w": 200,
      "h": 40,
      "type": "button"
    }
  ],
  "ils": {...},
  "outputs": {
    "html_tailwind": "...",
    "html_plain": "...",
    "css": "...",
    "react": "...",
    "dart": "..."
  }
}
```

## ⚠️ Common Issues & Fixes

### Issue 1: Model Not Loading
**Symptom:** `model_loaded: false` in health check

**Solutions:**
1. Verify file exists: `ls backend/models/ui_classification_model.h5`
2. Check file permissions
3. Verify TensorFlow is installed: `pip install tensorflow`
4. Check backend logs for detailed error

### Issue 2: TensorFlow Import Error
**Symptom:** `ModuleNotFoundError: No module named 'tensorflow'`

**Solution:**
```bash
cd backend
.venv\Scripts\Activate.ps1
pip install tensorflow>=2.13.0
```

### Issue 3: Port Already in Use
**Symptom:** `Error: Address already in use`

**Solutions:**
```bash
# Find process using port
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different ports
uvicorn app_new:app --reload --host 0.0.0.0 --port 8001
```

### Issue 4: CORS Errors
**Symptom:** Browser console shows CORS errors

**Solution:**
Check `backend/config.py` includes frontend URL:
```python
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### Issue 5: Low Classification Accuracy
**Symptom:** Wrong UI elements detected

**Solutions:**
1. Check if model is actually loaded
2. Verify model was trained on similar UI styles
3. Try with clearer, simpler UI screenshots
4. Check confidence threshold in `backend/utils/tf_classifier.py`
5. Consider retraining model with more data

## 📊 Performance Benchmarks

Expected performance metrics:

- **Backend Startup:** < 5 seconds
- **Model Loading:** < 2 seconds
- **Image Processing:** 1-3 seconds per screenshot
- **Frontend Load:** < 1 second
- **API Response Time:** 100-500ms (excluding model inference)

## 🎯 Success Criteria

Your project is working correctly if:

- [x] Backend starts without errors
- [x] Model loads successfully (check logs)
- [x] Frontend displays properly
- [x] File upload works
- [x] Code generation completes
- [x] All output formats are generated
- [x] No console errors
- [x] Classification results look reasonable

## 📝 Next Steps After Verification

Once everything works:

1. **Test with Real Data**
   - Upload various UI screenshots
   - Test different layouts (forms, buttons, cards)
   - Verify accuracy across different UI styles

2. **Monitor Performance**
   - Check processing time
   - Monitor memory usage
   - Watch for any errors in logs

3. **Gather Feedback**
   - Test with actual design screenshots
   - Note which elements classify correctly
   - Identify edge cases or issues

4. **Iterate**
   - Collect misclassified examples
   - Add to training dataset
   - Retrain model for better accuracy

5. **Deploy**
   - Set up production environment
   - Configure production settings
   - Set up monitoring and logging

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check the detailed logs in terminal
2. Review `backend/MODEL_INTEGRATION.md`
3. Check `QUICKSTART.md` for quick fixes
4. Verify all dependencies are installed
5. Try with a simple, clear UI screenshot first

## 📚 Documentation References

- **Quick Start:** `QUICKSTART.md`
- **Model Integration:** `backend/MODEL_INTEGRATION.md`
- **Project Report:** `PROJECT_REPORT.md`
- **API Docs:** `http://localhost:8000/docs` (when running)

---

**Last Updated:** November 20, 2025

Remember: The system will work even without the model (using fallback classifier), but accuracy will be significantly better with your trained model properly loaded!
