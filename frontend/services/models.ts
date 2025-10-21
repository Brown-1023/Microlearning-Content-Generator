import axios from 'axios';
import Cookies from 'js-cookie';
import { isNgrok } from '../utils/axios-config';

export interface ModelInfo {
  name: string;
  category: string;
  display_name: string;
  requires_key: string;
}

export interface ModelRestrictions {
  enabled: boolean;
  allowed_models: string[];
}

export interface ModelsResponse {
  models: ModelInfo[];
  all_models?: Record<string, ModelInfo>;
  restrictions?: ModelRestrictions;
}

class ModelService {
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

  /**
   * Get available models for the current user
   */
  async getAvailableModels(): Promise<ModelsResponse | null> {
    try {
      const response = await axios.get(`${this.baseURL}/api/models`, {
        headers: this.getHeaders()
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to get models:', error);
      return null;
    }
  }

  /**
   * Update model restrictions (admin only)
   */
  async updateRestrictions(enabled: boolean, allowedModels: string[]): Promise<{
    success: boolean;
    message?: string;
    restrictions?: ModelRestrictions;
  }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/models/restrictions`,
        {
          enabled,
          allowed_models: allowedModels
        },
        { headers: this.getHeaders() }
      );
      return {
        success: true,
        message: response.data.message,
        restrictions: response.data.restrictions
      };
    } catch (error: any) {
      console.error('Failed to update model restrictions:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to update model restrictions'
      };
    }
  }
}

export const modelService = new ModelService();
