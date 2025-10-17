import axios from 'axios';
import Cookies from 'js-cookie';
import { isNgrok } from '../utils/axios-config';

const TOKEN_KEY = 'auth_token';

class AuthService {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || '';
  
  // Configure axios to always include the token
  constructor() {
    this.setupAxiosInterceptor();
  }

  private setupAxiosInterceptor() {
    // Add a request interceptor to include the token and ngrok header (if needed) in all requests
    axios.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        // Only add ngrok-skip-browser-warning header if using ngrok
        if (isNgrok) {
          config.headers['ngrok-skip-browser-warning'] = 'true';
        }
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY);
  }

  private setToken(token: string): void {
    // Set token with 24 hour expiry
    Cookies.set(TOKEN_KEY, token, { expires: 1, sameSite: 'strict' });
  }

  private removeToken(): void {
    Cookies.remove(TOKEN_KEY);
  }

  async checkAuth(): Promise<boolean> {
    try {
      const token = this.getToken();
      if (!token) {
        return false;
      }

      const headers: Record<string, string> = {
        'Authorization': `Bearer ${token}`
      };
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.get(`${this.baseURL}/api/auth/check`, { headers });
      return response.status === 200;
    } catch {
      // Token is invalid or expired
      this.removeToken();
      return false;
    }
  }

  async login(password: string): Promise<boolean> {
    try {
      const headers: Record<string, string> = {};
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.post(
        `${this.baseURL}/api/auth/login`,
        { password },
        { headers }
      );
      
      if (response.status === 200 && response.data.token) {
        this.setToken(response.data.token);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  async logout(): Promise<void> {
    try {
      const headers: Record<string, string> = {};
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      await axios.post(
        `${this.baseURL}/api/auth/logout`,
        {},
        { headers }
      );
    } catch {
      // Ignore errors
    }
    // Always remove token on logout
    this.removeToken();
  }
}

export const authService = new AuthService();