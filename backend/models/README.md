# Model Directory

This directory contains the trained TensorFlow/Keras model for UI element classification.

## Required Model File

Place your trained model file here:
- **Filename:** `ui_classification_model.h5`
- **Type:** TensorFlow/Keras model (.h5 format)

## How to Add Your Model

1. Copy your trained `ui_classification_model.h5` file to this directory:
   ```
   backend/models/ui_classification_model.h5
   ```

2. Ensure the model was trained with the following class labels (in order):
   - background
   - button
   - card
   - heading
   - image_block
   - input_field
   - link
   - password_input
   - text_block

3. The model should expect input shape: `(None, 224, 224, 3)`
   - RGB images normalized to [0, 1]
   - Size: 224x224 pixels

## Model Training

If you need to train the model, refer to your training scripts. The model should be saved using:

```python
model.save('ui_classification_model.h5')
```

## Fallback Behavior

If the model file is not found:
- The system will automatically use a geometric-based fallback classifier
- A warning will be logged at startup
- The API will continue to function with reduced accuracy
