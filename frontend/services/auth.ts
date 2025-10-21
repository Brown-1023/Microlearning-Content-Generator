import axios from 'axios';
import Cookies from 'js-cookie';
import { isNgrok } from '../utils/axios-config';

const TOKEN_KEY = 'auth_token';
const ROLE_KEY = 'user_role';

export type UserRole = 'admin' | 'editor' | null;

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

  private setRole(role: UserRole): void {
    if (role) {
      Cookies.set(ROLE_KEY, role, { expires: 1, sameSite: 'strict' });
    }
  }

  private removeRole(): void {
    Cookies.remove(ROLE_KEY);
  }

  getRole(): UserRole {
    const role = Cookies.get(ROLE_KEY);
    return (role as UserRole) || null;
  }

  async checkAuth(): Promise<{ authenticated: boolean; role: UserRole }> {
    try {
      const token = this.getToken();
      if (!token) {
        return { authenticated: false, role: null };
      }

      const headers: Record<string, string> = {
        'Authorization': `Bearer ${token}`
      };
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.get(`${this.baseURL}/api/auth/check`, { headers });
      if (response.status === 200 && response.data) {
        const role = response.data.role as UserRole;
        this.setRole(role);
        return { authenticated: true, role };
      }
      return { authenticated: false, role: null };
    } catch {
      // Token is invalid or expired
      this.removeToken();
      this.removeRole();
      return { authenticated: false, role: null };
    }
  }

  async login(password: string): Promise<{ success: boolean; role: UserRole }> {
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
        const role = response.data.role as UserRole;
        this.setRole(role);
        return { success: true, role };
      }
      return { success: false, role: null };
    } catch {
      return { success: false, role: null };
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
    // Always remove token and role on logout
    this.removeToken();
    this.removeRole();
  }
}

export const authService = new AuthService();