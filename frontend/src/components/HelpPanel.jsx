import React, { useState } from 'react';

const HelpPanel = () => {
  const [isOpen, setIsOpen] = useState(false);

  const shortcuts = [
    { key: 'Ctrl + O', description: 'Open file dialog' },
    { key: 'Ctrl + Enter', description: 'Generate code' },
    { key: 'Ctrl + C', description: 'Copy current code' },
    { key: 'Ctrl + S', description: 'Download current code' },
    { key: '1-5', description: 'Switch between tabs' },
  ];

  const features = [
    '🎨 Multi-framework code generation',
    '📱 Responsive design detection',
    '⚡ Real-time preview',
    '💾 Easy download & copy',
    '🖱️ Drag & drop support',
    '⌨️ Keyboard shortcuts'
  ];

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 w-12 h-12 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200 hover:scale-110 z-40"
        aria-label="Help"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-200">Help & Features</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-slate-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Keyboard Shortcuts */}
              <div>
                <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <span>⌨️</span> Keyboard Shortcuts
                </h3>
                <div className="space-y-3">
                  {shortcuts.map((shortcut, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                      <span className="text-sm text-slate-300">{shortcut.description}</span>
                      <kbd className="px-2 py-1 bg-slate-700 text-slate-200 rounded text-xs font-mono">
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <span>✨</span> Features
                </h3>
                <div className="space-y-2">
                  {features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-3 p-2 text-slate-300 text-sm">
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Usage Guide */}
            <div className="mt-8 pt-6 border-t border-slate-800">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <span>🚀</span> How to Use
              </h3>
              <ol className="space-y-2 text-slate-300 text-sm">
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">1</span>
                  <span>Upload a UI screenshot or design mockup</span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">2</span>
                  <span>Click "Generate Code" to analyze your design</span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">3</span>
                  <span>Switch between different code formats using the tabs</span>
                </li>
                <li className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs">4</span>
                  <span>Copy or download the generated code for your project</span>
                </li>
              </ol>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default HelpPanel;