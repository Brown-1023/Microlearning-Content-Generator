import axios from 'axios';
import Cookies from 'js-cookie';
import { isNgrok } from '../utils/axios-config';

interface GenerationParams {
  content_type: string;
  generator_model: string;
  input_text: string;
  num_questions: number;
  focus_areas: string | null;
  generator_temperature?: number;
  generator_top_p?: number;
  formatter_temperature?: number;
  formatter_top_p?: number;
}

interface StreamProgress {
  stage: string;
  message: string;
  progress: number;
  draft?: string;
}

interface StreamCallback {
  onProgress?: (data: StreamProgress) => void;
  onDraft?: (draft: string) => void;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

interface DefaultPrompts {
  mcq_generator: string;
  mcq_formatter: string;
  nmcq_generator: string;
  nmcq_formatter: string;
  summary_generator: string;
  summary_formatter: string;
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
          timeout: 360000 // 6 minutes timeout
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

  async generateContentStream(
    params: GenerationParams,
    callbacks: StreamCallback
  ): Promise<void> {
    const headers = this.getHeaders();
    headers['Accept'] = 'text/event-stream';
    
    const eventSource = new EventSource(
      `${this.baseURL}/run/stream`,
      {
        // @ts-ignore - EventSource doesn't natively support headers, but we'll use a workaround
        withCredentials: true
      }
    );

    // Use fetch with EventSource polyfill for headers support
    const response = await fetch(`${this.baseURL}/run/stream`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.text();
      callbacks.onError?.(`Failed to start streaming: ${error}`);
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    if (!reader) {
      callbacks.onError?.('Stream reader not available');
      return;
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            const eventType = line.substring(6).trim();
            continue;
          }
          
          if (line.startsWith('data:')) {
            const data = line.substring(5).trim();
            if (data === '[DONE]') {
              return;
            }
            
            try {
              const parsedData = JSON.parse(data);
              const eventLine = lines[lines.indexOf(line) - 1];
              const eventType = eventLine?.startsWith('event:') 
                ? eventLine.substring(6).trim() 
                : 'message';

              switch (eventType) {
                case 'progress':
                  callbacks.onProgress?.(parsedData);
                  break;
                case 'draft':
                  callbacks.onDraft?.(parsedData.draft || '');
                  callbacks.onProgress?.(parsedData);
                  break;
                case 'complete':
                  callbacks.onComplete?.(parsedData);
                  break;
                case 'error':
                  callbacks.onError?.(parsedData.error);
                  break;
                default:
                  if (parsedData.stage) {
                    callbacks.onProgress?.(parsedData);
                  }
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (error: any) {
      callbacks.onError?.(`Stream error: ${error.message}`);
    } finally {
      reader.releaseLock();
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

  async getCurrentPrompts(): Promise<DefaultPrompts | null> {
    try {
      const response = await axios.get(`${this.baseURL}/api/prompts`, { 
        headers: this.getHeaders() 
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch current prompts:', error);
      return null;
    }
  }

  async getDefaultPrompts(): Promise<DefaultPrompts | null> {
    try {
      const response = await axios.get(`${this.baseURL}/api/prompts/defaults`, { 
        headers: this.getHeaders() 
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch default prompts:', error);
      return null;
    }
  }

  async resetPromptsToDefaults(): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/prompts/reset`,
        {},
        { headers: this.getHeaders() }
      );
      return { 
        success: response.data.success, 
        message: response.data.message || 'Prompts reset to defaults successfully' 
      };
    } catch (error: any) {
      console.error('Failed to reset prompts:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to reset prompts' 
      };
    }
  }

  async updateDefaultPrompts(): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/prompts/update-defaults`,
        {},
        { headers: this.getHeaders() }
      );
      return { 
        success: response.data.success, 
        message: response.data.message || 'Default prompts updated successfully' 
      };
    } catch (error: any) {
      console.error('Failed to update default prompts:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to update default prompts' 
      };
    }
  }

  async reformatContent(params: {
    draft_1: string;
    input_text?: string;
    content_type: string;
    generator_model: string;
    num_questions: number;
    focus_areas?: string | null;
    formatter_temperature?: number;
    formatter_top_p?: number;
  }): Promise<any> {
    try {
      const response = await axios.post(
        `${this.baseURL}/reformat`,
        params,
        { 
          headers: this.getHeaders(),
          timeout: 60000 // 1 minute timeout
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

  async savePrompts(prompts: DefaultPrompts): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/api/prompts`,
        prompts,
        { headers: this.getHeaders() }
      );
      return { success: true, message: 'Prompts saved successfully' };
    } catch (error: any) {
      console.error('Failed to save prompts:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Failed to save prompts' 
      };
    }
  }
}

export const generationService = new GenerationService();
export type { DefaultPrompts, GenerationParams, StreamProgress, StreamCallback };