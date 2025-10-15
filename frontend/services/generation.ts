import axios from 'axios';

interface GenerationParams {
  content_type: string;
  generator_model: string;
  input_text: string;
  num_questions: number;
  focus_areas: string | null;
}

class GenerationService {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || '';

  async generateContent(params: GenerationParams): Promise<any> {
    try {
      const response = await axios.post(
        `${this.baseURL}/run`,
        params,
        { 
          withCredentials: true,
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
}

export const generationService = new GenerationService();
