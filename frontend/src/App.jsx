import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Play,
  Square,
  RefreshCw,
  Settings,
  BarChart3,
  Shield
} from 'lucide-react'
import Dashboard from './components/Dashboard'
import Positions from './components/Positions'
import Delta from './components/Delta'
import Tasks from './components/Tasks'
import Config from './components/Config'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [botStatus, setBotStatus] = useState('stopped')
  const [lastUpdate, setLastUpdate] = useState(null)

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'positions', name: 'Positions', icon: Activity },
    { id: 'delta', name: 'Delta', icon: TrendingUp },
    { id: 'tasks', name: 'Tasks', icon: Settings },
    { id: 'config', name: 'Config', icon: Settings },
  ]

  const startBot = async () => {
    try {
      const response = await axios.post('/api/start')
      if (response.data.status === 'started') {
        setBotStatus('running')
      }
    } catch (error) {
      console.error('Failed to start bot:', error)
    }
  }

  const stopBot = async () => {
    try {
      const response = await axios.post('/api/stop')
      if (response.data.status === 'stopped') {
        setBotStatus('stopped')
      }
    } catch (error) {
      console.error('Failed to stop bot:', error)
    }
  }

  useEffect(() => {
    // Check bot status on mount
    const checkStatus = async () => {
      try {
        const response = await axios.get('/api/state')
        setBotStatus(response.data.running ? 'running' : 'stopped')
        setLastUpdate(new Date())
      } catch (error) {
        console.error('Failed to check bot status:', error)
      }
    }
    
    checkStatus()
    
    // Update status every 15 seconds
    const interval = setInterval(checkStatus, 15000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-primary-600" />
              <h1 className="ml-3 text-xl font-semibold text-gray-900">
                The Hedger
              </h1>
              <span className="ml-2 text-sm text-gray-500">
                Automated LP Position Hedging Bot
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  botStatus === 'running' ? 'bg-success-500' : 'bg-danger-500'
                }`} />
                <span className="text-sm font-medium">
                  {botStatus === 'running' ? 'Running' : 'Stopped'}
                </span>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={startBot}
                  disabled={botStatus === 'running'}
                  className="btn-success flex items-center space-x-1 disabled:opacity-50"
                >
                  <Play className="h-4 w-4" />
                  <span>Start</span>
                </button>
                <button
                  onClick={stopBot}
                  disabled={botStatus === 'stopped'}
                  className="btn-danger flex items-center space-x-1 disabled:opacity-50"
                >
                  <Square className="h-4 w-4" />
                  <span>Stop</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'positions' && <Positions />}
        {activeTab === 'delta' && <Delta />}
        {activeTab === 'tasks' && <Tasks />}
        {activeTab === 'config' && <Config />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center text-sm text-gray-500">
            <span>Phase 1 - Sample Data</span>
            {lastUpdate && (
              <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            )}
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 