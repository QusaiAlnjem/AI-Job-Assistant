export const API_BASE_URL = "http://127.0.0.1:8000/api";

export const ENDPOINTS = {
    LOGIN: `${API_BASE_URL}/users/login/`,
    SIGNUP: `${API_BASE_URL}/users/register/`,
    PROFILE: `${API_BASE_URL}/users/profile/`,
    RESUMES: `${API_BASE_URL}/resumes/`,
    JOB_MATCHES: `${API_BASE_URL}/jobs/matches/`,
    JOB_SEARCH: `${API_BASE_URL}/jobs/search/`,
}

// Simple helper to get the token
export function getToken() {
    return localStorage.getItem('auth_token');
}