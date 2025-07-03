import React from 'react'
import { useAuth } from '../contexts/AuthContext'

const Dashboard = () => {
  const { user } = useAuth()

  console.log('Dashboard: Renderizando para usuário:', user?.email)

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Bem-vindo ao UTM Tracker SaaS, {user?.name || user?.email}!</p>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Total de Campanhas</h3>
          <div className="stat-value">0</div>
        </div>
        
        <div className="stat-card">
          <h3>Bots do Telegram</h3>
          <div className="stat-value">0</div>
        </div>
        
        <div className="stat-card">
          <h3>Leads Capturados</h3>
          <div className="stat-value">0</div>
        </div>
        
        <div className="stat-card">
          <h3>Taxa de Conversão</h3>
          <div className="stat-value">0%</div>
        </div>
      </div>

      <div style={{ 
        background: 'white', 
        padding: '2rem', 
        borderRadius: '10px', 
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)' 
      }}>
        <h2>🎉 Parabéns!</h2>
        <p>Seu UTM Tracker SaaS está funcionando perfeitamente!</p>
        <p>Agora você pode começar a configurar suas campanhas e bots do Telegram.</p>
        
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderRadius: '5px' }}>
          <h3>Próximos passos:</h3>
          <ul style={{ marginLeft: '1rem', marginTop: '0.5rem' }}>
            <li>Criar seu primeiro bot do Telegram</li>
            <li>Configurar uma campanha de UTM</li>
            <li>Gerar links de convite rastreáveis</li>
            <li>Monitorar os leads em tempo real</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

