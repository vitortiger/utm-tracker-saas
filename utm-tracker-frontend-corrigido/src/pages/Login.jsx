import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    console.log('Login: Verificando se usuário já está autenticado')
    if (isAuthenticated) {
      console.log('Login: Usuário já autenticado, redirecionando para dashboard')
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    console.log('Login: Formulário submetido')
    
    setError('')
    setLoading(true)

    if (!email || !password) {
      setError('Por favor, preencha todos os campos')
      setLoading(false)
      return
    }

    try {
      console.log('Login: Tentando fazer login com:', email)
      const result = await login(email, password)
      
      if (result.success) {
        console.log('Login: Sucesso, redirecionando para dashboard')
        navigate('/dashboard')
      } else {
        console.log('Login: Falha:', result.error)
        setError(result.error || 'Erro ao fazer login')
      }
    } catch (error) {
      console.error('Login: Erro:', error)
      setError('Erro interno do sistema')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>UTM Tracker SaaS</h1>
          <p>Rastreamento de UTMs no Telegram</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Sua senha"
              disabled={loading}
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Não tem uma conta? {' '}
            <Link to="/register">Registre-se aqui</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login

