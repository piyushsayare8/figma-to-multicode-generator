import React from 'react';

const ProgressBar = ({ progress, isVisible, label }) => {
  if (!isVisible) return null;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-200">{label}</span>
        <span className="text-sm text-slate-400">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300 ease-out relative overflow-hidden"
          style={{ width: `${Math.min(progress, 100)}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;