import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import type { LoginCredentials } from '../services/authService';
import { initializeGoogleAuth, GOOGLE_CLIENT_ID } from '../config/googleAuth';
import { useAuth } from '../contexts/AuthContext';
import VideoBackground from '../components/VideoBackground';
import AnimatedHeadline from '../components/AnimatedHeadline';
import AnimatedForm from '../components/AnimatedForm';
import AnimatedInput from '../components/AnimatedInput';
import AnimatedButton from '../components/AnimatedButton';

const Login: React.FC = () => {
  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const { login } = useAuth();

  useEffect(() => {
    // Check if user is already authenticated
    if (authService.isAuthenticated()) {
      navigate('/dashboard');
      return;
    }

    // Initialize Google OAuth
    const setupGoogleAuth = async () => {
      try {
        await initializeGoogleAuth();
        
        if (window.google && googleButtonRef.current) {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleLogin,
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          window.google.accounts.id.renderButton(googleButtonRef.current, {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'signin_with',
            shape: 'rectangular',
            logo_alignment: 'left',
          });
        }
      } catch (error) {
        console.error('Google Auth initialization failed:', error);
        // Hide Google button if initialization fails
        if (googleButtonRef.current) {
          googleButtonRef.current.innerHTML = '<p class="text-white/60 text-sm">Google Sign-in unavailable</p>';
        }
      }
    };

    setupGoogleAuth();
  }, [navigate]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
  };

  const handleGoogleLogin = async (response: any) => {
    setLoading(true);
    setError('');

    try {
      const result = await authService.googleLogin(response.credential);
      
      if (result.success && result.user) {
        login(result.user);
        navigate('/dashboard');
      } else {
        setError(result.message || 'Google login failed');
      }
    } catch (error) {
      setError('Google login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    try {
      const result = await authService.login(formData);
      
      if (result.success && result.user) {
        login(result.user);
        navigate('/dashboard');
      } else {
        setError(result.message || 'Login failed');
      }
    } catch (error) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <VideoBackground>
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Panel - Animated Branding */}
          <div className="hidden lg:block">
            <AnimatedHeadline
              title="Welcome to Navo"
              subtitle="Your AI-powered research companion that transforms how you discover, analyze, and collaborate on research projects."
              features={[
                "Advanced AI research capabilities",
                "Secure data management",
                "Collaborative research tools",
                "Real-time insights and analytics"
              ]}
            />
          </div>

          {/* Mobile Branding - Shown only on mobile */}
          <div className="lg:hidden mb-8">
            <AnimatedHeadline
              title="Welcome to Navo"
              subtitle="Your AI-powered research companion"
              features={[
                "Advanced AI research capabilities",
                "Secure data management",
                "Collaborative research tools"
              ]}
            />
          </div>

          {/* Right Panel - Animated Login Form */}
          <div className="w-full flex justify-center">
            <AnimatedForm
              title="Welcome Back"
              subtitle="Sign in to your Navo account"
            >
              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-xl">
                  <p className="text-red-200 text-sm flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{error}</span>
                  </p>
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email Input */}
                <AnimatedInput
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  label="Email Address"
                  placeholder="Enter your email"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                    </svg>
                  }
                  required
                />

                {/* Password Input */}
                <AnimatedInput
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  label="Password"
                  placeholder="Enter your password"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  }
                  rightIcon={
                    showPassword ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    )
                  }
                  onRightIconClick={() => setShowPassword(!showPassword)}
                  required
                />

                {/* Remember Me & Forgot Password */}
                <div className="flex items-center justify-between">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="h-4 w-4 text-blue-400 focus:ring-blue-400/50 border-white/30 rounded bg-white/10"
                    />
                    <span className="text-sm text-white/80">Remember me</span>
                  </label>
                  <Link to="/forgot-password" className="text-sm text-blue-300 hover:text-blue-200 transition-colors">
                    Forgot password?
                  </Link>
                </div>

                {/* Login Button */}
                <AnimatedButton
                  type="submit"
                  loading={loading}
                  className="w-full"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                  }
                >
                  {loading ? 'Signing in...' : 'Sign In'}
                </AnimatedButton>
              </form>

              {/* Divider */}
              <div className="my-8">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/20" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-transparent text-white/60">Or continue with</span>
                  </div>
                </div>
              </div>

              {/* Google Login Button */}
              <div ref={googleButtonRef} className="w-full"></div>

              {/* Signup Link */}
              <div className="mt-8 text-center">
                <p className="text-white/80">
                  Don't have an account?{' '}
                  <Link to="/signup" className="text-blue-300 hover:text-blue-200 font-medium transition-colors">
                    Sign up for free
                  </Link>
                </p>
              </div>
            </AnimatedForm>
          </div>
        </div>
      </div>
    </VideoBackground>
  );
};

export default Login;
