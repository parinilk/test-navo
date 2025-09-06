import React, { useState, forwardRef } from 'react';

interface AnimatedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  icon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onRightIconClick?: () => void;
}

const AnimatedInput = forwardRef<HTMLInputElement, AnimatedInputProps>(
  ({ label, error, icon, rightIcon, onRightIconClick, className = "", ...props }, ref) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleFocus = () => setIsFocused(true);
  const handleBlur = () => setIsFocused(false);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (props.onChange) props.onChange(e);
  };

    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-white/90 mb-2">
          {label}
        </label>
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            {...props}
            onFocus={handleFocus}
            onBlur={handleBlur}
            onChange={handleChange}
            className={`
              w-full px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl
              text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50
              focus:border-blue-400/50 transition-all duration-300
              ${icon ? 'pl-12' : ''}
              ${rightIcon ? 'pr-12' : ''}
              ${error ? 'border-red-400/50 focus:ring-red-400/50 focus:border-red-400/50' : ''}
              ${className}
            `}
            placeholder={props.placeholder}
          />
          {rightIcon && (
            <button
              type="button"
              onClick={onRightIconClick}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white/80 transition-colors duration-200"
            >
              {rightIcon}
            </button>
          )}
          
          {/* Animated Border */}
          <div className={`absolute inset-0 rounded-xl border-2 border-transparent transition-all duration-300 pointer-events-none ${
            isFocused ? 'border-blue-400/50' : ''
          }`}></div>
        </div>
        
        {error && (
          <p className="text-red-400 text-sm flex items-center space-x-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </p>
        )}
      </div>
    );
  }
);

AnimatedInput.displayName = 'AnimatedInput';

export default AnimatedInput;
