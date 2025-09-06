import React, { useState, useEffect } from 'react';

interface VideoBackgroundProps {
  children: React.ReactNode;
  videoSrc?: string;
  fallbackImage?: string;
}

const VideoBackground: React.FC<VideoBackgroundProps> = ({ 
  children, 
  videoSrc = "https://gnjtnxzwzlmbopyipzjz.supabase.co/storage/v1/object/sign/vide1/SaaS_Login_Page_Video_Generation.mp4?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xMzUyNDZlZC03YjVhLTQ2MGEtOWE3NC00ZTNmNWU4ZjA3ZGMiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJ2aWRlMS9TYWFTX0xvZ2luX1BhZ2VfVmlkZW9fR2VuZXJhdGlvbi5tcDQiLCJpYXQiOjE3NTcxNzI4MzIsImV4cCI6MTc1OTc2NDgzMn0.cIPDpsMOBF2pEWfdt7722FCdBYdLbcoREb3XSHlVa8o",
  fallbackImage = "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=2074&q=80"
}) => {
  const [isMobile, setIsMobile] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [videoLoading, setVideoLoading] = useState(true);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Video Background */}
      <div className="absolute inset-0 z-0">
        {!isMobile && !videoError ? (
          <video
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
            poster={fallbackImage}
            onLoadStart={() => {
              console.log('Video loading started');
              setVideoLoading(true);
            }}
            onCanPlay={() => {
              console.log('Video can play');
              setVideoLoading(false);
            }}
            onError={(e) => {
              console.error('Video loading error:', e);
              setVideoError(true);
              setVideoLoading(false);
            }}
            onLoad={() => {
              console.log('Video loaded successfully');
              setVideoLoading(false);
            }}
          >
            <source src={videoSrc} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        ) : (
          <div 
            className="w-full h-full bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: `url(${fallbackImage})` }}
          />
        )}
        
        {/* Video Loading Indicator */}
        {!isMobile && videoLoading && !videoError && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <div className="text-white text-lg">Loading video...</div>
          </div>
        )}
        
        {/* Video Error Indicator */}
        {!isMobile && videoError && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <div className="text-white text-lg">Video failed to load, using fallback image</div>
          </div>
        )}
        
        {/* Video Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-black/60 via-purple-900/40 to-blue-900/60"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
      </div>

      {/* Animated Background Elements - Reduced on mobile for performance */}
      <div className="absolute inset-0 z-10">
        {!isMobile && (
          <>
            {/* Floating Particles */}
            <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-white/20 rounded-full animate-pulse"></div>
            <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-blue-400/30 rounded-full animate-bounce"></div>
            <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-purple-400/20 rounded-full animate-ping"></div>
            <div className="absolute top-2/3 right-1/4 w-1.5 h-1.5 bg-cyan-400/25 rounded-full animate-pulse"></div>
            <div className="absolute bottom-1/3 left-1/4 w-2.5 h-2.5 bg-pink-400/15 rounded-full animate-bounce"></div>
            
            {/* Geometric Shapes */}
            <div className="absolute top-20 right-20 w-32 h-32 border border-white/10 rounded-full animate-spin-slow"></div>
            <div className="absolute bottom-20 left-20 w-24 h-24 border border-white/5 rounded-full animate-pulse"></div>
            <div className="absolute top-1/2 left-1/4 w-16 h-16 border border-white/8 rounded-full animate-ping"></div>
            
            {/* Gradient Orbs */}
            <div className="absolute top-1/4 right-1/4 w-40 h-40 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-full blur-xl animate-pulse"></div>
            <div className="absolute bottom-1/4 left-1/4 w-32 h-32 bg-gradient-to-r from-cyan-500/10 to-pink-500/10 rounded-full blur-xl animate-bounce"></div>
          </>
        )}
        
        {/* Minimal mobile particles */}
        {isMobile && (
          <>
            <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-white/30 rounded-full animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-1 h-1 bg-blue-400/40 rounded-full animate-bounce"></div>
          </>
        )}
      </div>

      {/* Content */}
      <div className="relative z-20">
        {children}
      </div>
    </div>
  );
};

export default VideoBackground;
