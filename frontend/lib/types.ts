export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface Project {
  id: number;
  name: string;
  url: string;
  description?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface ScrapeResult {
  id: number;
  project_id: number;
  url: string;
  status: string;
  summary: string;
  key_points: string[];
  entities?: Record<string, string[]>;
  topics?: string[];
  scrape_method: string;
  ai_provider: string;
  error_message?: string;
  created_at: string;
}

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface FormField {
  type: string;
  name: string;
  id?: string;
  placeholder?: string;
  required: boolean;
  value?: string;
  options?: { value: string; text: string }[];
}

export interface UserResponse {
  id: number;
  email: string;
  is_active: boolean;
  projects?: Project[];
}

export interface DetectedForm {
  formIndex: number;
  action: string;
  method: string;
  fields: FormField[];
}
