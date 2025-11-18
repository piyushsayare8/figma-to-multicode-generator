import React, { useState } from 'react';

const Tooltip = ({ children, content, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  };

  const arrowClasses = {
    top: 'top-full left-1/2 transform -translate-x-1/2 border-t-slate-800 border-t-4 border-x-transparent border-x-4 border-b-0',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 border-b-slate-800 border-b-4 border-x-transparent border-x-4 border-t-0',
    left: 'left-full top-1/2 transform -translate-y-1/2 border-l-slate-800 border-l-4 border-y-transparent border-y-4 border-r-0',
    right: 'right-full top-1/2 transform -translate-y-1/2 border-r-slate-800 border-r-4 border-y-transparent border-y-4 border-l-0',
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className={`absolute z-50 px-3 py-2 text-sm text-slate-200 bg-slate-800 border border-slate-700 rounded-lg shadow-lg whitespace-nowrap ${positionClasses[position]} animate-fade-in-up`}>
          {content}
          <div className={`absolute w-0 h-0 ${arrowClasses[position]}`}></div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;