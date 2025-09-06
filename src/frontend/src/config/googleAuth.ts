// Google OAuth Configuration
export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || 'your-google-client-id';

// Google OAuth scopes
export const GOOGLE_SCOPES = [
  'openid',
  'profile',
  'email'
];

// Initialize Google OAuth
export const initializeGoogleAuth = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: () => {}, // Will be set by components
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        resolve();
      } else {
        reject(new Error('Google Identity Services failed to load'));
      }
    };
    
    script.onerror = () => {
      reject(new Error('Failed to load Google Identity Services script'));
    };
    
    document.head.appendChild(script);
  });
};

// Google OAuth button configuration
export const getGoogleButtonConfig = (callback: (response: any) => void) => ({
  client_id: GOOGLE_CLIENT_ID,
  callback,
  auto_select: false,
  cancel_on_tap_outside: true,
});

// Declare global types for Google Identity Services
declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: (notification: any) => void) => void;
          renderButton: (element: Element, config: any) => void;
          disableAutoSelect: () => void;
        };
      };
    };
  }
}

