import React from 'react';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          UTM Tracker SaaS
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Rastreamento de UTMs no Telegram
        </p>
        <div className="space-x-4">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Login
          </button>
          <button className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300">
            Registrar
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

