import axios from '../utils/axios-config';

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

export const modelService = {
  /**
   * Get available models for the current user
   */
  async getAvailableModels(): Promise<ModelsResponse | null> {
    try {
      const response = await axios.get('/api/models');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get models:', error);
      return null;
    }
  },

  /**
   * Update model restrictions (admin only)
   */
  async updateRestrictions(enabled: boolean, allowedModels: string[]): Promise<{
    success: boolean;
    message?: string;
    restrictions?: ModelRestrictions;
  }> {
    try {
      const response = await axios.post('/api/models/restrictions', {
        enabled,
        allowed_models: allowedModels
      });
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
};
