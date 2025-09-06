import React, { useEffect, useState } from 'react';

interface AnimatedHeadlineProps {
  title: string;
  subtitle: string;
  features: string[];
  className?: string;
}

const AnimatedHeadline: React.FC<AnimatedHeadlineProps> = ({ 
  title, 
  subtitle, 
  features, 
  className = "" 
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 300);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`text-center space-y-6 lg:space-y-8 ${className}`}>
      {/* Main Title with Typewriter Effect */}
      <div className="space-y-3 lg:space-y-4">
        <h1 className={`text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white transition-all duration-1000 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        }`}>
          <span className="bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent animate-gradient-x">
            {title}
          </span>
        </h1>
        
        {/* Animated Underline */}
        <div className={`h-1 w-24 sm:w-32 bg-gradient-to-r from-blue-400 to-purple-500 mx-auto rounded-full transition-all duration-1000 delay-500 ${
          isVisible ? 'opacity-100 scale-x-100' : 'opacity-0 scale-x-0'
        }`}></div>
      </div>

      {/* Subtitle with Fade In */}
      <p className={`text-lg sm:text-xl lg:text-2xl text-white/90 max-w-2xl mx-auto px-4 transition-all duration-1000 delay-700 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        {subtitle}
      </p>

      {/* Features List with Staggered Animation */}
      <div className="space-y-3 lg:space-y-4 max-w-lg mx-auto px-4">
        {features.map((feature, index) => (
          <div
            key={index}
            className={`flex items-center space-x-3 lg:space-x-4 text-base lg:text-lg text-white/80 transition-all duration-500 ${
              isVisible 
                ? 'opacity-100 translate-x-0' 
                : 'opacity-0 -translate-x-8'
            }`}
            style={{ transitionDelay: `${900 + index * 200}ms` }}
          >
            <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full animate-pulse flex-shrink-0"></div>
            <span className="font-medium text-left">{feature}</span>
          </div>
        ))}
      </div>

      {/* Floating Elements - Hidden on mobile for better performance */}
      <div className="hidden lg:block absolute top-10 right-10 w-32 h-32 border border-white/20 rounded-full animate-spin-slow"></div>
      <div className="hidden lg:block absolute bottom-10 left-10 w-24 h-24 border border-white/10 rounded-full animate-pulse"></div>
      <div className="hidden lg:block absolute top-1/2 left-1/4 w-16 h-16 border border-white/15 rounded-full animate-ping"></div>
    </div>
  );
};

export default AnimatedHeadline;
