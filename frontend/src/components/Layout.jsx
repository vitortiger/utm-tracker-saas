import React from 'react'
import { useAuth } from '../contexts/AuthContext'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()

  const handleLogout = () => {
    console.log('Layout: Fazendo logout')
    logout()
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          UTM Tracker SaaS
        </div>
        <div className="navbar-user">
          <span>Olá, {user?.name || user?.email}</span>
          <button className="btn-logout" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout

