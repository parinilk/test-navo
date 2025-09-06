import React, { useState, useEffect } from 'react';

interface AnimatedFormProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
  className?: string;
}

const AnimatedForm: React.FC<AnimatedFormProps> = ({ 
  children, 
  title, 
  subtitle, 
  className = "" 
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <div className={`bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-8 transition-all duration-1000 ${
        isVisible ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-8 scale-95'
      }`}>
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className={`text-3xl font-bold text-white mb-2 transition-all duration-700 delay-200 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}>
            {title}
          </h2>
          <p className={`text-white/80 transition-all duration-700 delay-400 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}>
            {subtitle}
          </p>
        </div>

        {/* Form Content */}
        <div className={`transition-all duration-700 delay-600 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default AnimatedForm;
