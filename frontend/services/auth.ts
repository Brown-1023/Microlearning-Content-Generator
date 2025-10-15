import axios from 'axios';
import Cookies from 'js-cookie';

class AuthService {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || '';

  async checkAuth(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/api/auth/check`, {
        withCredentials: true
      });
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async login(password: string): Promise<boolean> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/auth/login`,
        { password },
        { withCredentials: true }
      );
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async logout(): Promise<void> {
    try {
      await axios.post(
        `${this.baseURL}/api/auth/logout`,
        {},
        { withCredentials: true }
      );
    } catch {
      // Ignore errors
    }
    Cookies.remove('session_id');
  }
}

export const authService = new AuthService();
