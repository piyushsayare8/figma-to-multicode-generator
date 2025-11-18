import { useEffect } from 'react';

const useKeyboardShortcuts = (handlers) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Check if any input/textarea is focused
      const isInputFocused = document.activeElement.tagName === 'INPUT' || 
                           document.activeElement.tagName === 'TEXTAREA';
      
      if (isInputFocused) return;

      const key = event.key.toLowerCase();
      const ctrl = event.ctrlKey || event.metaKey;
      const shift = event.shiftKey;

      Object.keys(handlers).forEach(shortcut => {
        const [keys, callback] = handlers[shortcut];
        const [modifier, mainKey] = keys.split('+');
        
        if (modifier === 'ctrl' && ctrl && key === mainKey) {
          event.preventDefault();
          callback();
        } else if (modifier === 'shift' && shift && key === mainKey) {
          event.preventDefault();
          callback();
        } else if (!modifier && !ctrl && !shift && key === keys) {
          event.preventDefault();
          callback();
        }
      });
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
};

export default useKeyboardShortcuts;