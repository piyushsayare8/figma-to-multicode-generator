# Figma to Multicode Generator ✨

A sophisticated AI-powered system that converts UI screenshots into multiple code formats using Computer Vision (OpenCV) and a trained CNN model (TensorFlow/Keras).

## 🚀 Features

### Multi-Framework Support
- **HTML + Tailwind CSS** - Modern utility-first styling
- **HTML + CSS** - Classic vanilla CSS approach
- **React JSX** - Component-based React code
- **Flutter/Dart** - Cross-platform mobile development

### AI-Powered Classification
- 🧠 **Trained TensorFlow Model** for accurate UI element detection
- 🎯 **9 UI Element Types**: button, input, text, heading, image, card, link, password input, and background
- 📊 **Confidence Scoring** for prediction reliability
- 🔄 **Automatic Fallback** to geometric classifier if model unavailable

### Enhanced User Experience
- 🎨 **Modern Dark UI** with gradient backgrounds and glass morphism
- 📁 **Drag & Drop Support** for seamless file uploads
- ⚡ **Real-time Progress Tracking** with animated progress bars
- 🔔 **Smart Notifications** for user feedback
- 💡 **Tooltips & Help Panel** for better usability
- ⌨️ **Keyboard Shortcuts** for power users
- 📱 **Fully Responsive Design** across all devices
- 🎯 **Demo Mode** to try the interface without backend

### Advanced UI Components
- Animated loading spinners with dual rotation
- Success animations and visual feedback
- Enhanced code viewer with syntax highlighting
- Interactive tab system with icons and descriptions
- File size validation and format checking
- Copy-to-clipboard with visual confirmation

## 🎮 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + O` | Open file dialog |
| `Ctrl + Enter` | Generate code |
| `Ctrl + C` | Copy current code |
| `Ctrl + S` | Download current code |
| `1-5` | Switch between tabs |

## 🛠️ Project Structure

```
├── backend/              # FastAPI server
│   ├── app_new.py       # Main API application
│   ├── config.py        # Configuration settings
│   ├── requirements.txt # Python dependencies
│   ├── models/          # Trained model directory
│   │   ├── ui_classification_model.h5  # Your trained model
│   │   └── README.md    # Model placement instructions
│   └── utils/           # Core processing modules
│       ├── tf_classifier.py   # TensorFlow model integration
│       ├── detection.py       # OpenCV block detection
│       ├── generator_*.py     # Code generators
│       └── ils_builder.py     # Layout schema builder
├── frontend/            # React + Vite application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   │   ├── Notification.jsx  # Toast notifications
│   │   │   ├── ProgressBar.jsx   # Loading progress
│   │   │   ├── Tooltip.jsx       # Interactive tooltips
│   │   │   └── HelpPanel.jsx     # Help & shortcuts
│   │   ├── hooks/       # Custom React hooks
│   │   │   └── useKeyboardShortcuts.js
│   │   ├── App.jsx      # Main application
│   │   ├── DemoApp.jsx  # Demo wrapper
│   │   ├── index.css    # Enhanced styles & animations
│   │   └── main.jsx     # Application entry point
│   └── package.json     # Frontend dependencies
└── MODEL_INTEGRATION.md # Detailed model integration guide
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Trained model file: `ui_classification_model.h5`

### Step 1: Setup Trained Model

1. **Place your trained model** in the backend models directory:
   ```bash
   cp ui_classification_model.h5 backend/models/
   ```

2. **Verify model specifications**:
   - Input shape: `(None, 224, 224, 3)`
   - 9 output classes (background, button, card, heading, image_block, input_field, link, password_input, text_block)

📖 See [MODEL_INTEGRATION.md](backend/MODEL_INTEGRATION.md) for detailed integration guide.

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate environment
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Install dependencies (includes TensorFlow)
pip install -r requirements.txt

# Start the server
uvicorn app_new:app --reload --host 0.0.0.0 --port 8000
```

**Or use the automated script (Windows):**
```bash
.\run_backend.ps1
```

### Step 3: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173` with the backend API at `http://localhost:8000`.

## 🎯 How to Use

1. **Upload Design**: Drag & drop or click to upload a UI screenshot
2. **Generate Code**: Click "Generate Code" or press `Ctrl + Enter`
3. **View Results**: Switch between different code formats using tabs (1-5 keys)
4. **Copy/Download**: Use the action buttons or keyboard shortcuts

## 🎨 UI Enhancements

### Visual Improvements
- **Gradient backgrounds** with animated floating elements
- **Glass morphism effects** for modern card design
- **Smooth animations** and transitions throughout
- **Custom scrollbars** matching the dark theme
- **Enhanced typography** with Inter font family

### Interactive Elements
- **Hover effects** with scale transformations
- **Loading animations** with dual rotating spinners
- **Success confirmations** with animated checkmarks
- **Error handling** with contextual error messages

### Accessibility Features
- **Focus management** and keyboard navigation
- **ARIA labels** for screen readers
- **Reduced motion** support for accessibility
- **High contrast** mode compatibility

## 🔧 Configuration

Update `src/config.js` to customize the API endpoint:

```javascript
export const API_BASE_URL = "http://localhost:8000"; // or your backend URL
```

## 🎪 Demo Mode

Try the interface without setting up the backend:
1. Click the "Try Demo Mode" button in the top-left corner
2. Upload any image and click "Generate Code"
3. Explore all the features with simulated data

## 📱 Responsive Design

The interface automatically adapts to:
- **Desktop**: Full multi-column layout with all features
- **Tablet**: Stacked layout with optimized spacing
- **Mobile**: Single-column responsive design

## 🚀 Performance

- **Optimized animations** with CSS transforms and GPU acceleration
- **Lazy loading** for better initial load times
- **Efficient state management** with minimal re-renders
- **Debounced interactions** to prevent excessive API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your enhancements
4. Test thoroughly across devices
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using React, Tailwind CSS, and modern web technologies**

## 5. Technical Architecture

### Backend Pipeline

1. **Image Upload** → User uploads UI screenshot via API
2. **OpenCV Detection** → Detects UI element bounding boxes
3. **TensorFlow Classification** → Trained model classifies each element
4. **Style Analysis** → Extracts colors, spacing, and visual properties
5. **ILS Builder** → Creates Intermediate Layout Schema
6. **Code Generation** → Generates code in multiple frameworks

### Model Training Process

The CNN model was trained with:
- **Dataset**: Real and synthetic UI screenshots
- **Classes**: 9 UI element types
- **Architecture**: Custom CNN with transfer learning
- **Training**: 30-100 epochs on labeled UI components
- **Validation**: Accuracy and confidence scoring

### Classification Classes

| Class           | Description              | UI Type     |
|-----------------|--------------------------|-------------|
| background      | Background containers    | container   |
| button          | Action buttons           | button      |
| card            | Card components          | card        |
| heading         | Heading text             | heading     |
| image_block     | Image placeholders       | image       |
| input_field     | Text input fields        | text_input  |
| link            | Hyperlinks               | link        |
| password_input  | Password input fields    | text_input  |
| text_block      | Regular text content     | text        |

## 6. Notes & Customization

### Model Integration
- Place your trained `.h5` model in `backend/models/`
- System automatically falls back to geometric classifier if model unavailable
- Adjust confidence threshold in `tf_classifier.py` if needed

### Extending the System
- **Add new frameworks**: Create new generator in `utils/generator_*.py`
- **Improve detection**: Enhance OpenCV logic in `detection.py`
- **Retrain model**: Use more training data for better accuracy
- **Custom UI elements**: Update CLASS_NAMES and retrain model
