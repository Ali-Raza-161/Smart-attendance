import axios from 'axios'
export const api = axios.create({ baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api' })
api.interceptors.request.use((c) => { const t = localStorage.getItem('sa_token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c })
export const get = (u: string) => api.get(u).then(r => r.data)
export const post = (u: string, d?: any) => api.post(u, d).then(r => r.data)
export const patch = (u: string, d?: any) => api.patch(u, d).then(r => r.data)
export const del = (u: string) => api.delete(u).then(r => r.data)
