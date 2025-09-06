import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import type { SignupCredentials } from '../services/authService';
import { initializeGoogleAuth, GOOGLE_CLIENT_ID } from '../config/googleAuth';
import { useAuth } from '../contexts/AuthContext';
import VideoBackground from '../components/VideoBackground';
import AnimatedHeadline from '../components/AnimatedHeadline';
import AnimatedForm from '../components/AnimatedForm';
import AnimatedInput from '../components/AnimatedInput';
import AnimatedButton from '../components/AnimatedButton';

const Signup: React.FC = () => {
  const [formData, setFormData] = useState<SignupCredentials>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
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
            callback: handleGoogleSignup,
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          window.google.accounts.id.renderButton(googleButtonRef.current, {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'signup_with',
            shape: 'rectangular',
            logo_alignment: 'left',
          });
        }
      } catch (error) {
        console.error('Google Auth initialization failed:', error);
      }
    };

    setupGoogleAuth();
  }, [navigate]);

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
  };

  const getPasswordStrengthColor = (strength: number): string => {
    if (strength <= 2) return 'bg-red-400';
    if (strength <= 3) return 'bg-yellow-400';
    if (strength <= 4) return 'bg-blue-400';
    return 'bg-green-400';
  };

  const getPasswordStrengthText = (strength: number): string => {
    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Fair';
    if (strength <= 4) return 'Good';
    return 'Strong';
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
    
    setError(''); // Clear error when user types
  };

  const handleGoogleSignup = async (response: any) => {
    setLoading(true);
    setError('');

    try {
      const result = await authService.googleLogin(response.credential);
      
      if (result.success && result.user) {
        login(result.user);
        navigate('/dashboard');
      } else {
        setError(result.message || 'Google signup failed');
      }
    } catch (error) {
      setError('Google signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    if (!acceptTerms) {
      setError('Please accept the terms and conditions');
      setLoading(false);
      return;
    }

    try {
      const result = await authService.signup(formData);
      
      if (result.success && result.user) {
        login(result.user);
        navigate('/dashboard');
      } else {
        setError(result.message || 'Signup failed');
      }
    } catch (error) {
      setError('Signup failed. Please try again.');
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
              title="Join Navo Today"
              subtitle="Start your AI-powered research journey and unlock the full potential of intelligent research collaboration."
              features={[
                "Free account with premium features",
                "Unlimited research projects",
                "24/7 AI assistance",
                "Advanced collaboration tools"
              ]}
            />
          </div>

          {/* Mobile Branding - Shown only on mobile */}
          <div className="lg:hidden mb-8">
            <AnimatedHeadline
              title="Join Navo Today"
              subtitle="Start your AI-powered research journey"
              features={[
                "Free account with premium features",
                "Unlimited research projects",
                "24/7 AI assistance"
              ]}
            />
          </div>

          {/* Right Panel - Animated Signup Form */}
          <div className="w-full flex justify-center">
            <AnimatedForm
              title="Create Account"
              subtitle="Join thousands of researchers using Navo"
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

              {/* Signup Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Full Name Input */}
                <AnimatedInput
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  label="Full Name"
                  placeholder="Enter your full name"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  }
                  required
                />

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
                <div className="space-y-2">
                  <AnimatedInput
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    label="Password"
                    placeholder="Create a strong password"
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
                  
                  {/* Password Strength Indicator */}
                  {formData.password && (
                    <div className="mt-2">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs text-white/60">Password strength:</span>
                        <span className={`text-xs font-medium ${
                          passwordStrength <= 2 ? 'text-red-400' : 
                          passwordStrength <= 3 ? 'text-yellow-400' : 
                          passwordStrength <= 4 ? 'text-blue-400' : 'text-green-400'
                        }`}>
                          {getPasswordStrengthText(passwordStrength)}
                        </span>
                      </div>
                      <div className="w-full bg-white/20 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${getPasswordStrengthColor(passwordStrength)}`}
                          style={{ width: `${(passwordStrength / 5) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Confirm Password Input */}
                <div className="space-y-2">
                  <AnimatedInput
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    label="Confirm Password"
                    placeholder="Confirm your password"
                    icon={
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    }
                    rightIcon={
                      showConfirmPassword ? (
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
                    onRightIconClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    required
                  />
                  
                  {/* Password Match Indicator */}
                  {formData.confirmPassword && (
                    <div className="mt-1">
                      {formData.password === formData.confirmPassword ? (
                        <p className="text-xs text-green-400 flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Passwords match
                        </p>
                      ) : (
                        <p className="text-xs text-red-400 flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          Passwords don't match
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Terms and Conditions */}
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    id="acceptTerms"
                    checked={acceptTerms}
                    onChange={(e) => setAcceptTerms(e.target.checked)}
                    className="h-4 w-4 text-purple-400 focus:ring-purple-400/50 border-white/30 rounded bg-white/10 mt-1"
                  />
                  <label htmlFor="acceptTerms" className="text-sm text-white/80">
                    I agree to the{' '}
                    <Link to="/terms" className="text-purple-300 hover:text-purple-200 transition-colors">
                      Terms of Service
                    </Link>{' '}
                    and{' '}
                    <Link to="/privacy" className="text-purple-300 hover:text-purple-200 transition-colors">
                      Privacy Policy
                    </Link>
                  </label>
                </div>

                {/* Signup Button */}
                <AnimatedButton
                  type="submit"
                  loading={loading}
                  className="w-full"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                  }
                >
                  {loading ? 'Creating account...' : 'Create Account'}
                </AnimatedButton>
              </form>

              {/* Divider */}
              <div className="my-8">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-white/20" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-transparent text-white/60">Or sign up with</span>
                  </div>
                </div>
              </div>

              {/* Google Signup Button */}
              <div ref={googleButtonRef} className="w-full"></div>

              {/* Login Link */}
              <div className="mt-8 text-center">
                <p className="text-white/80">
                  Already have an account?{' '}
                  <Link to="/login" className="text-purple-300 hover:text-purple-200 font-medium transition-colors">
                    Sign in here
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

export default Signup;
