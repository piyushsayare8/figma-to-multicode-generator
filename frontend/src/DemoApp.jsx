import React, { useState } from 'react';
import App from './App';

const demoData = {
  layout: [
    { type: 'button', x: 100, y: 50, w: 120, h: 40 },
    { type: 'input', x: 50, y: 120, w: 200, h: 30 },
    { type: 'text', x: 80, y: 180, w: 150, h: 20 },
    { type: 'image', x: 300, y: 50, w: 100, h: 100 }
  ],
  outputs: {
    html_tailwind: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Demo Form</h2>
        <div class="space-y-4">
            <input type="text" placeholder="Enter your name" 
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            <button class="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-md transition duration-200">
                Submit
            </button>
            <p class="text-gray-600 text-sm">This is a demo generated interface</p>
        </div>
    </div>
</body>
</html>`,
    html_plain: `<!DOCTYPE html>
<html>
<head>
    <title>Demo UI</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h2>Demo Form</h2>
        <input type="text" placeholder="Enter your name">
        <button>Submit</button>
        <p>This is a demo generated interface</p>
    </div>
</body>
</html>`,
    css: `.container {
    max-width: 400px;
    margin: 50px auto;
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

h2 {
    color: #333;
    margin-bottom: 20px;
}

input {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

button {
    width: 100%;
    padding: 12px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.2s;
}

button:hover {
    background: #2563eb;
}`,
    react: `import React, { useState } from 'react';

const GeneratedPage = () => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(\`Hello, \${inputValue}!\`);
  };

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 mt-12">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Demo Form</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Enter your name"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-md transition duration-200"
        >
          Submit
        </button>
        <p className="text-gray-600 text-sm">This is a demo generated interface</p>
      </form>
    </div>
  );
};

export default GeneratedPage;`,
    dart: `import 'package:flutter/material.dart';

class GeneratedPage extends StatefulWidget {
  @override
  _GeneratedPageState createState() => _GeneratedPageState();
}

class _GeneratedPageState extends State<GeneratedPage> {
  final TextEditingController _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: Center(
        child: Container(
          width: 350,
          padding: EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.black12,
                blurRadius: 8,
                offset: Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Demo Form',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[800],
                ),
              ),
              SizedBox(height: 16),
              TextField(
                controller: _controller,
                decoration: InputDecoration(
                  hintText: 'Enter your name',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Hello, \${_controller.text}!')),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  padding: EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: Text('Submit', style: TextStyle(color: Colors.white)),
              ),
              SizedBox(height: 12),
              Text(
                'This is a demo generated interface',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}`
  }
};

// Demo mode wrapper
const DemoApp = () => {
  const [isDemoMode, setIsDemoMode] = useState(false);

  if (isDemoMode) {
    // Override the API call to return demo data
    const originalFetch = window.fetch;
    window.fetch = (url, options) => {
      if (url.includes('/analyze')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(demoData)
        });
      }
      return originalFetch(url, options);
    };
  }

  return (
    <>
      <div className="fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsDemoMode(!isDemoMode)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            isDemoMode 
              ? 'bg-green-500 hover:bg-green-600 text-white' 
              : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
          }`}
        >
          {isDemoMode ? '🎯 Demo Mode ON' : '🚀 Try Demo Mode'}
        </button>
      </div>
      <App />
    </>
  );
};

export default DemoApp;