import React, { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../lib/auth'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    console.log('AuthProvider: Verificando autenticação inicial')
    const token = authService.getToken()
    const currentUser = authService.getCurrentUser()
    
    if (token && currentUser) {
      console.log('AuthProvider: Usuário autenticado encontrado:', currentUser.email)
      setUser(currentUser)
    } else {
      console.log('AuthProvider: Nenhum usuário autenticado')
    }
    
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    console.log('AuthContext: Tentando login')
    setLoading(true)
    
    try {
      const result = await authService.login(email, password)
      
      if (result.success) {
        setUser(result.user)
        console.log('AuthContext: Login bem-sucedido')
        return { success: true }
      } else {
        console.log('AuthContext: Falha no login:', result.error)
        return { success: false, error: result.error }
      }
    } catch (error) {
      console.error('AuthContext: Erro no login:', error)
      return { success: false, error: 'Erro interno do sistema' }
    } finally {
      setLoading(false)
    }
  }

  const register = async (name, email, password) => {
    console.log('AuthContext: Tentando registro')
    setLoading(true)
    
    try {
      const result = await authService.register(name, email, password)
      
      if (result.success) {
        setUser(result.user)
        console.log('AuthContext: Registro bem-sucedido')
        return { success: true }
      } else {
        console.log('AuthContext: Falha no registro:', result.error)
        return { success: false, error: result.error }
      }
    } catch (error) {
      console.error('AuthContext: Erro no registro:', error)
      return { success: false, error: 'Erro interno do sistema' }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    console.log('AuthContext: Fazendo logout')
    authService.logout()
    setUser(null)
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

