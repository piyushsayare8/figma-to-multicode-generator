# Figma to Multicode Generator ✨

A sophisticated Computer Vision + CNN + template-based system that converts UI screenshots into multiple code outputs with an enhanced, modern user experience.

## 🚀 Features

### Multi-Framework Support
- **HTML + Tailwind CSS** - Modern utility-first styling
- **HTML + CSS** - Classic vanilla CSS approach
- **React JSX** - Component-based React code
- **Flutter/Dart** - Cross-platform mobile development

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
│   ├── app.py           # Main API application
│   ├── config.py        # Configuration settings
│   ├── requirements.txt # Python dependencies
│   └── utils/           # Core processing modules
│       ├── classifier.py      # CNN classification
│       ├── detection.py       # OpenCV detection
│       ├── generator_*.py     # Code generators
│       └── ils_builder.py     # Layout builder
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
```

## 🚀 Getting Started

### Backend Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

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

## 4. Typical Flow

1. Start the backend (FastAPI).
2. Start the frontend (Vite).
3. Open the frontend, upload a UI screenshot (PNG/JPG).
4. Backend:
   - Uses OpenCV to detect candidate UI blocks.
   - Classifies each block (stub or your CNN).
   - Builds an Intermediate Layout Schema (ILS) from blocks.
   - Generates multi-code output from ILS (HTML/Tailwind, HTML+CSS, React, Dart).
5. Frontend displays:
   - Live HTML/Tailwind preview in an iframe.
   - Tabs for viewing and copying each code variant.
   - Download buttons for raw code.

## 5. Notes

- This is a **starter production-style project**. You are expected to:
  - Build & train the CNN for UI block classification.
  - Improve detection heuristics and ILS logic for more complex layouts.
- All core pieces are modular and testable.
