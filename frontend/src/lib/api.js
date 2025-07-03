import axios from 'axios'

// Configuração da API
const API_BASE_URL = 'https://utm-tracker-saas-utm-tracker-app.c0fl94.easypanel.host/api'

console.log('API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('Fazendo requisição:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Erro na requisição:', error)
    return Promise.reject(error)
  }
)

// Interceptor para tratar respostas
api.interceptors.response.use(
  (response) => {
    console.log('Resposta recebida:', response.status, response.data)
    return response
  },
  (error) => {
    console.error('Erro na resposta:', error.response?.status, error.response?.data)
    
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default api

