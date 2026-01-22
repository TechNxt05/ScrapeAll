import axios from 'axios';
import { API_URL } from './types';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const scrapeWebsite = async (
    url: string,
    projectName?: string,
    projectId?: number,
    selector?: string
) => {
    const response = await api.post('/api/scrape', {
        url,
        project_name: projectName,
        project_id: projectId,
        selector: selector
    });
    return response.data;
};

export const getProjects = async () => {
    const response = await api.get('/api/projects');
    return response.data;
};

export const getProject = async (id: number) => {
    const response = await api.get(`/api/projects/${id}`);
    return response.data;
};

export const chatWithContent = async (projectId: number, message: string) => {
    const response = await api.post('/api/chat', { project_id: projectId, message });
    return response.data;
};

export const detectForms = async (url: string) => {
    const response = await api.post('/api/forms/detect', { url });
    return response.data;
};

export const getChatHistory = async (projectId: number) => {
    const response = await api.get(`/api/chat/${projectId}/history`);
    return response.data;
};

export const getLatestScrape = async (projectId: number) => {
    try {
        const response = await api.get(`/api/projects/${projectId}/latest-scrape`);
        return response.data;
    } catch (e: any) {
        if (e.response?.status === 404) return null; // Project not found or no scrapes
        // If response is null (body), it might be valid "no scrape" result depending on backend
        // My backend returns null response body or JSON? 
        // Backend logic: "if not scrape: return None". FastAPI returns "null" JSON.
        return null;
    }
};

export const getProjectScrapes = async (projectId: number) => {
    const response = await api.get(`/api/projects/${projectId}/scrapes`);
    return response.data;
};
