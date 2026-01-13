/**
 * Smart Classroom AI - API Client Configuration
 */

import axios from 'axios'
import { supabase } from './supabase'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 60000 // 60 seconds - increased for AI model processing
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      supabase.auth.signOut()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
