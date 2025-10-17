import axios from 'axios';
import Cookies from 'js-cookie';
import { isNgrok } from '../utils/axios-config';

interface GenerationParams {
  content_type: string;
  generator_model: string;
  input_text: string;
  num_questions: number;
  focus_areas: string | null;
  temperature?: number;
  top_p?: number;
  custom_mcq_generator?: string | null;
  custom_mcq_formatter?: string | null;
  custom_nmcq_generator?: string | null;
  custom_nmcq_formatter?: string | null;
}

interface DefaultPrompts {
  mcq_generator: string;
  mcq_formatter: string;
  nmcq_generator: string;
  nmcq_formatter: string;
}

class GenerationService {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || '';

  private getHeaders(): Record<string, string> {
    const token = Cookies.get('auth_token');
    const headers: Record<string, string> = {};
    
    // Only add ngrok header if we're using ngrok
    if (isNgrok) {
      headers['ngrok-skip-browser-warning'] = 'true';
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async generateContent(params: GenerationParams): Promise<any> {
    try {
      const response = await axios.post(
        `${this.baseURL}/run`,
        params,
        { 
          headers: this.getHeaders(),
          timeout: 120000 // 2 minutes timeout
        }
      );
      return response.data;
    } catch (error: any) {
      if (error.response) {
        return error.response.data;
      }
      throw error;
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const headers: Record<string, string> = {};
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.get(`${this.baseURL}/healthz`, { headers });
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async getVersion(): Promise<any> {
    try {
      const headers: Record<string, string> = {};
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.get(`${this.baseURL}/version`, { headers });
      return response.data;
    } catch {
      return null;
    }
  }

  async getDefaultPrompts(): Promise<DefaultPrompts | null> {
    try {
      const headers: Record<string, string> = {};
      if (isNgrok) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }
      const response = await axios.get(`${this.baseURL}/api/prompts`, { headers });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch default prompts:', error);
      return null;
    }
  }
}

export const generationService = new GenerationService();
export type { DefaultPrompts, GenerationParams };