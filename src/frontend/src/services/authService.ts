import Cookies from 'js-cookie';

// Types for authentication
export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  googleId?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  success: boolean;
  user?: User;
  token?: string;
  message?: string;
}

class AuthService {
  private baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'; // Adjust to your backend URL
  
  // Get current user from token
  getCurrentUser(): User | null {
    const token = this.getToken();
    if (!token) return null;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
        googleId: payload.googleId
      };
    } catch (error) {
      console.error('Error parsing token:', error);
      return null;
    }
  }

  // Get auth token
  getToken(): string | undefined {
    return Cookies.get('auth_token');
  }

  // Set auth token
  setToken(token: string): void {
    Cookies.set('auth_token', token, { 
      expires: 7, // 7 days
      secure: true,
      sameSite: 'strict'
    });
  }

  // Remove auth token
  removeToken(): void {
    Cookies.remove('auth_token');
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  // Login with email and password
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (data.success && data.token) {
        this.setToken(data.token);
        return {
          success: true,
          user: data.user,
          token: data.token
        };
      }

      return {
        success: false,
        message: data.message || 'Login failed'
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        message: 'Network error occurred'
      };
    }
  }

  // Signup with email and password
  async signup(credentials: SignupCredentials): Promise<AuthResponse> {
    try {
      if (credentials.password !== credentials.confirmPassword) {
        return {
          success: false,
          message: 'Passwords do not match'
        };
      }

      const response = await fetch(`${this.baseURL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: credentials.name,
          email: credentials.email,
          password: credentials.password
        }),
      });

      const data = await response.json();

      if (data.success && data.token) {
        this.setToken(data.token);
        return {
          success: true,
          user: data.user,
          token: data.token
        };
      }

      return {
        success: false,
        message: data.message || 'Signup failed'
      };
    } catch (error) {
      console.error('Signup error:', error);
      return {
        success: false,
        message: 'Network error occurred'
      };
    }
  }

  // Google OAuth login
  async googleLogin(credential: string): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credential }),
      });

      const data = await response.json();

      if (data.success && data.token) {
        this.setToken(data.token);
        return {
          success: true,
          user: data.user,
          token: data.token
        };
      }

      return {
        success: false,
        message: data.message || 'Google login failed'
      };
    } catch (error) {
      console.error('Google login error:', error);
      return {
        success: false,
        message: 'Network error occurred'
      };
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      await fetch(`${this.baseURL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.removeToken();
    }
  }

  // Refresh token
  async refreshToken(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`
        }
      });

      const data = await response.json();

      if (data.success && data.token) {
        this.setToken(data.token);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }
}

export const authService = new AuthService();
