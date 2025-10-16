import axios from 'axios';
import Cookies from 'js-cookie';

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

  private getAuthHeader(): Record<string, string> {
    const token = Cookies.get('auth_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async generateContent(params: GenerationParams): Promise<any> {
    try {
      const response = await axios.post(
        `${this.baseURL}/run`,
        params,
        { 
          headers: this.getAuthHeader(),
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
      const response = await axios.get(`${this.baseURL}/healthz`);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async getVersion(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseURL}/version`);
      return response.data;
    } catch {
      return null;
    }
  }

  async getDefaultPrompts(): Promise<DefaultPrompts | null> {
    try {
      const response = await axios.get(`${this.baseURL}/api/prompts`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch default prompts:', error);
      return null;
    }
  }
}

export const generationService = new GenerationService();
export type { DefaultPrompts, GenerationParams };