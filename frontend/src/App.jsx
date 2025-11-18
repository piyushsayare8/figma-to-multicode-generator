import React, { useState, useRef, useEffect } from "react";
import { API_BASE_URL } from "./config";
import Notification from "./components/Notification";
import ProgressBar from "./components/ProgressBar";
import Tooltip from "./components/Tooltip";
import HelpPanel from "./components/HelpPanel";
import useKeyboardShortcuts from "./hooks/useKeyboardShortcuts";

const TABS = [
  { 
    id: "preview", 
    label: "Live Preview", 
    icon: "👁️",
    description: "See your generated UI in action"
  },
  { 
    id: "html_tw", 
    label: "HTML + Tailwind", 
    icon: "🎨",
    description: "Modern utility-first CSS framework"
  },
  { 
    id: "html_css", 
    label: "HTML + CSS", 
    icon: "📄",
    description: "Classic HTML with custom styles"
  },
  { 
    id: "react", 
    label: "React JSX", 
    icon: "⚛️",
    description: "Component-based React code"
  },
  { 
    id: "dart", 
    label: "Flutter", 
    icon: "📱",
    description: "Cross-platform mobile code"
  },
];

// Loading animation component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center">
    <div className="relative">
      <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      <div className="absolute inset-0 w-8 h-8 border-4 border-transparent border-r-purple-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '0.8s' }}></div>
    </div>
  </div>
);

// Success animation component
const SuccessCheck = () => (
  <div className="flex items-center justify-center">
    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-bounce">
      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7"></path>
      </svg>
    </div>
  </div>
);

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("preview");
  const [copySuccess, setCopySuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [notification, setNotification] = useState({ isVisible: false, message: "", type: "success" });
  const fileInputRef = useRef(null);

  // Show notification helper
  const showNotification = (message, type = "success") => {
    setNotification({ isVisible: true, message, type });
  };

  // Hide notification
  const hideNotification = () => {
    setNotification(prev => ({ ...prev, isVisible: false }));
  };

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+o': ['ctrl+o', () => fileInputRef.current?.click()],
    'ctrl+enter': ['ctrl+enter', () => file && handleAnalyze()],
    'ctrl+c': ['ctrl+c', () => result && activeTab !== 'preview' && handleCopy()],
    'ctrl+s': ['ctrl+s', () => result && activeTab !== 'preview' && handleDownload()],
    '1': ['1', () => setActiveTab('preview')],
    '2': ['2', () => setActiveTab('html_tw')],
    '3': ['3', () => setActiveTab('html_css')],
    '4': ['4', () => setActiveTab('react')],
    '5': ['5', () => setActiveTab('dart')]
  });

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const droppedFile = files[0];
      if (droppedFile.type.startsWith('image/')) {
        setFile(droppedFile);
        setResult(null);
        setError("");
      } else {
        setError("Please drop an image file.");
      }
    }
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      if (f.size > 10 * 1024 * 1024) { // 10MB limit
        setError("File size must be less than 10MB");
        showNotification("File too large! Please choose a file under 10MB.", "error");
        return;
      }
      if (!f.type.startsWith('image/')) {
        setError("Please select an image file");
        showNotification("Invalid file type! Please select an image.", "error");
        return;
      }
      setFile(f);
      setResult(null);
      setError("");
      showNotification("Image selected successfully!", "success");
    } else {
      setFile(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select an image file.");
      showNotification("Please select an image first!", "warning");
      return;
    }
    
    setLoading(true);
    setError("");
    setResult(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 15;
        });
      }, 200);

      const res = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Analysis failed");
      }

      const data = await res.json();
      setResult(data);
      showNotification(`Analysis complete! Found ${data.layout.length} UI elements.`, "success");
    } catch (err) {
      const errorMessage = err.message || "Something went wrong";
      setError(errorMessage);
      showNotification(errorMessage, "error");
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const getCodeForTab = () => {
    if (!result) return "";
    const { outputs } = result;
    switch (activeTab) {
      case "html_tw":
        return outputs.html_tailwind;
      case "html_css":
        return `/* index.html */\n${outputs.html_plain}\n\n/* styles.css */\n${outputs.css}`;
      case "react":
        return outputs.react;
      case "dart":
        return outputs.dart;
      default:
        return "";
    }
  };

  const handleCopy = async () => {
    const code = getCodeForTab();
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code);
      setCopySuccess(true);
      showNotification("Code copied to clipboard!", "success");
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      setError("Copy failed - please try again");
      showNotification("Failed to copy code. Please try again.", "error");
    }
  };

  const handleDownload = () => {
    const code = getCodeForTab();
    if (!code) return;
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    let filename = "code.txt";
    if (activeTab === "html_tw") filename = "index_tailwind.html";
    if (activeTab === "html_css") filename = "html_and_css.txt";
    if (activeTab === "react") filename = "GeneratedPage.jsx";
    if (activeTab === "dart") filename = "main.dart";
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showNotification(`Downloaded ${filename} successfully!`, "success");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950/20 to-slate-950 px-4 py-8 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
              Figma to Multicode Generator
            </h1>
          </div>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Transform your UI designs into production-ready code across multiple frameworks. 
            Simply upload a screenshot and watch the magic happen.
          </p>
          
          {/* Stats or features */}
          <div className="flex flex-wrap justify-center gap-6 mt-8">
            {[
              { icon: "⚡", label: "Instant Generation" },
              { icon: "🎯", label: "Multi-Framework" },
              { icon: "🛡️", label: "Production Ready" },
              { icon: "📱", label: "Responsive Design" }
            ].map((feature, index) => (
              <div key={index} className="flex items-center gap-2 text-sm text-slate-300">
                <span className="text-lg">{feature.icon}</span>
                <span>{feature.label}</span>
              </div>
            ))}
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Panel - Upload */}
          <div className="lg:col-span-4 space-y-6">
            {/* Upload Section */}
            <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-slate-200">Upload Design</h2>
              </div>

              {/* Drag & Drop Area */}
              <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
                  dragOver
                    ? "border-blue-400 bg-blue-500/10 scale-105"
                    : "border-slate-700 hover:border-slate-600 hover:bg-slate-800/30"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-slate-800 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-slate-200 font-medium">
                      {dragOver ? "Drop your image here!" : "Drag & drop or click to upload"}
                    </p>
                    <p className="text-sm text-slate-400 mt-1">
                      PNG, JPG, GIF up to 10MB
                    </p>
                  </div>
                </div>
              </div>

              {file && (
                <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-200 truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-slate-400">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              )}

              <button
                onClick={handleAnalyze}
                disabled={loading || !file}
                className="w-full mt-6 group relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-slate-700 disabled:to-slate-700 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <div className="flex items-center justify-center gap-3">
                  {loading ? <LoadingSpinner /> : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  )}
                  <span>{loading ? "Analyzing Design..." : "Generate Code"}</span>
                </div>
                {!loading && (
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-200"></div>
                )}
              </button>

              {/* Progress Bar */}
              <ProgressBar 
                progress={uploadProgress} 
                isVisible={loading} 
                label="Processing your design..."
              />

              {error && (
                <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Detection Results */}
            {result && (
              <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800/50 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <SuccessCheck />
                  </div>
                  <h2 className="text-lg font-semibold text-slate-200">Analysis Complete</h2>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                    <span className="text-sm text-slate-300">Detected Elements</span>
                    <span className="font-bold text-blue-400">{result.layout.length}</span>
                  </div>
                  
                  <div className="max-h-40 overflow-auto space-y-2">
                    {result.layout.map((block, idx) => (
                      <div key={idx} className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-slate-200">
                            {block.type.charAt(0).toUpperCase() + block.type.slice(1)}
                          </span>
                          <span className="text-xs text-slate-400">#{idx + 1}</span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                          {block.w} × {block.h} at ({block.x}, {block.y})
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Output */}
          <div className="lg:col-span-8 space-y-6">
            {/* Tab Navigation */}
            <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex flex-wrap gap-3">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`group relative flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                      activeTab === tab.id
                        ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105"
                        : "bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-slate-200 border border-slate-700/50"
                    }`}
                  >
                    <span className="text-lg">{tab.icon}</span>
                    <div className="text-left">
                      <div className="text-sm font-semibold">{tab.label}</div>
                      <div className="text-xs opacity-75">{tab.description}</div>
                    </div>
                    {activeTab === tab.id && (
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-20 rounded-xl"></div>
                    )}
                  </button>
                ))}
              </div>

              {/* Action buttons */}
              {activeTab !== "preview" && result && (
                <div className="flex gap-3 mt-6 pt-6 border-t border-slate-800">
                  <Tooltip content="Copy code to clipboard">
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-all duration-200 transform hover:scale-105"
                    >
                      {copySuccess ? (
                        <>
                          <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-green-400">Copied!</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span>Copy Code</span>
                        </>
                      )}
                    </button>
                  </Tooltip>
                  <Tooltip content="Download code as file">
                    <button
                      onClick={handleDownload}
                      className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white rounded-lg transition-all duration-200 transform hover:scale-105"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>Download</span>
                    </button>
                  </Tooltip>
                </div>
              )}
            </div>

            {/* Output Area */}
            <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800/50 rounded-2xl shadow-2xl overflow-hidden">
              <div className="h-[500px] lg:h-[600px]">
                {!result && !loading && (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8">
                    <div className="w-20 h-20 mx-auto mb-6 bg-slate-800 rounded-full flex items-center justify-center">
                      <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V3a1 1 0 011 1v8l-2 2-2-2V4a1 1 0 011-1m0 0H7m10 0v11a2 2 0 01-2 2H9a2 2 0 01-2-2V4" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-slate-300 mb-2">Ready to Generate</h3>
                    <p className="text-slate-500 max-w-md">
                      Upload a UI screenshot and click <span className="font-semibold text-blue-400">"Generate Code"</span> to see your results here.
                    </p>
                  </div>
                )}

                {loading && (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8">
                    <LoadingSpinner />
                    <h3 className="text-lg font-semibold text-slate-300 mt-6 mb-2">Analyzing Your Design</h3>
                    <p className="text-slate-500">Please wait while we process your image and generate the code...</p>
                  </div>
                )}

                {activeTab === "preview" && result && (
                  <div className="h-full bg-white rounded-xl m-4 overflow-hidden shadow-inner">
                    <iframe
                      title="Live Preview"
                      className="w-full h-full border-0"
                      srcDoc={result.outputs.html_tailwind}
                    />
                  </div>
                )}

                {activeTab !== "preview" && result && (
                  <div className="h-full p-4">
                    <div className="h-full bg-slate-950/80 rounded-xl border border-slate-800 overflow-hidden">
                      <div className="h-full flex flex-col">
                        {/* Code header */}
                        <div className="flex items-center justify-between px-4 py-3 bg-slate-900 border-b border-slate-800">
                          <div className="flex items-center gap-2">
                            <div className="flex gap-1">
                              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            </div>
                            <span className="text-sm font-medium text-slate-300 ml-2">
                              {TABS.find(t => t.id === activeTab)?.label}
                            </span>
                          </div>
                          <div className="text-xs text-slate-500">
                            {getCodeForTab().split('\n').length} lines
                          </div>
                        </div>
                        {/* Code content */}
                        <pre className="flex-1 p-4 text-sm text-slate-100 overflow-auto font-mono leading-relaxed">
                          <code>{getCodeForTab()}</code>
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Notification */}
        <Notification
          message={notification.message}
          type={notification.type}
          isVisible={notification.isVisible}
          onClose={hideNotification}
        />

        {/* Help Panel */}
        <HelpPanel />
      </div>
    </div>
  );
}
