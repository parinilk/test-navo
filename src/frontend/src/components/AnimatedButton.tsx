import React, { useState } from 'react';

interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  className = "",
  disabled,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);

  const baseClasses = `
    relative overflow-hidden rounded-xl font-medium transition-all duration-300
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent
    disabled:opacity-50 disabled:cursor-not-allowed
    transform active:scale-95 hover:scale-105
  `;

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-blue-500 to-purple-600 text-white
      hover:from-blue-600 hover:to-purple-700
      focus:ring-blue-400/50 shadow-lg hover:shadow-xl
    `,
    secondary: `
      bg-white/10 backdrop-blur-sm text-white border border-white/20
      hover:bg-white/20 hover:border-white/30
      focus:ring-white/50
    `,
    outline: `
      bg-transparent text-white border-2 border-white/30
      hover:bg-white/10 hover:border-white/50
      focus:ring-white/50
    `
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  return (
    <button
      {...props}
      disabled={disabled || loading}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
        ${isPressed ? 'scale-95' : ''}
      `}
    >
      {/* Ripple Effect */}
      <div className="absolute inset-0 bg-white/20 scale-0 rounded-full transition-transform duration-500 ease-out"></div>
      
      {/* Content */}
      <div className="relative flex items-center justify-center space-x-2">
        {loading ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        ) : (
          <>
            {icon && <span>{icon}</span>}
            <span>{children}</span>
          </>
        )}
      </div>
    </button>
  );
};

export default AnimatedButton;
