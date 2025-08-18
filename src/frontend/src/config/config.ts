// Configuration for the Navo frontend application

export const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  
  // App Information
  appName: import.meta.env.VITE_APP_NAME || 'Navo',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  
  // API Endpoints
  endpoints: {
    research: '/research',
    products: '/products',
    analytics: '/analytics'
  }
};

export default config;
