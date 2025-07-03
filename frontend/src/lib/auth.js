import api from './api'

export const authService = {
  async login(email, password) {
    console.log('Tentando fazer login com:', email)
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      })
      
      const { access_token, user } = response.data
      
      // Salvar token e dados do usuário
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      console.log('Login realizado com sucesso')
      return { success: true, user, token: access_token }
    } catch (error) {
      console.error('Erro no login:', error)
      const message = error.response?.data?.error || 'Erro ao fazer login'
      return { success: false, error: message }
    }
  },

  async register(name, email, password) {
    console.log('Tentando registrar usuário:', email)
    try {
      const response = await api.post('/auth/register', {
        name,
        email,
        password
      })
      
      const { access_token, user } = response.data
      
      // Salvar token e dados do usuário
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      console.log('Registro realizado com sucesso')
      return { success: true, user, token: access_token }
    } catch (error) {
      console.error('Erro no registro:', error)
      const message = error.response?.data?.error || 'Erro ao registrar usuário'
      return { success: false, error: message }
    }
  },

  logout() {
    console.log('Fazendo logout')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      console.error('Erro ao obter usuário atual:', error)
      return null
    }
  },

  getToken() {
    return localStorage.getItem('token')
  },

  isAuthenticated() {
    const token = this.getToken()
    const user = this.getCurrentUser()
    return !!(token && user)
  }
}

