import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  RefreshCw, 
  XCircle,
  Settings,
  Shield,
  Activity,
  AlertTriangle
} from 'lucide-react'

function Config() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchConfig = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/config')
      setConfig(response.data || {})
      setError(null)
    } catch (err) {
      setError('Failed to fetch configuration')
      console.error('Error fetching config:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfig()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <XCircle className="h-12 w-12 text-danger-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
        <p className="text-gray-500">{error}</p>
        <button onClick={fetchConfig} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }

  if (!config || Object.keys(config).length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No configuration available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Configuration</h2>
        <button 
          onClick={fetchConfig}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Blockchain Configuration */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-6 w-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Blockchain Settings</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Chain ID</p>
            <p className="text-sm text-gray-900">{config.blockchain?.chain_id || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">RPC URL</p>
            <p className="text-sm text-gray-900 font-mono truncate">
              {config.blockchain?.rpc_url || 'N/A'}
            </p>
          </div>
          <div className="md:col-span-2">
            <p className="text-sm font-medium text-gray-500">Wallet Address</p>
            <p className="text-sm text-gray-900 font-mono">
              {config.blockchain?.wallet_address || 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Hedging Configuration */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Activity className="h-6 w-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Hedging Settings</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Delta Threshold</p>
            <p className="text-sm text-gray-900">${config.hedging?.delta_threshold || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Rebalance Window</p>
            <p className="text-sm text-gray-900">{config.hedging?.rebalance_window || 'N/A'}s</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Max Slippage</p>
            <p className="text-sm text-gray-900">{config.hedging?.max_slippage || 'N/A'}%</p>
          </div>
        </div>
      </div>

      {/* Risk Management */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-warning-600" />
          <h3 className="text-lg font-semibold text-gray-900">Risk Management</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Max Leverage</p>
            <p className="text-sm text-gray-900">{config.risk?.max_leverage || 'N/A'}x</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Funding Cap APR</p>
            <p className="text-sm text-gray-900">{config.risk?.funding_cap_apr || 'N/A'}%</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">IL Cap</p>
            <p className="text-sm text-gray-900">{config.risk?.impermanent_loss_cap || 'N/A'}%</p>
          </div>
        </div>
      </div>

      {/* Dashboard Configuration */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Settings className="h-6 w-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Dashboard Settings</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Host</p>
            <p className="text-sm text-gray-900">{config.dashboard?.host || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Port</p>
            <p className="text-sm text-gray-900">{config.dashboard?.port || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Refresh Interval</p>
            <p className="text-sm text-gray-900">{config.dashboard?.refresh_interval || 'N/A'}s</p>
          </div>
        </div>
      </div>

      {/* Configuration Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Summary</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Configuration Status</span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
              Loaded
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Environment</span>
            <span className="text-sm text-gray-900">Production</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Phase</span>
            <span className="text-sm text-gray-900">Phase 1 - Sample Data</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Last Updated</span>
            <span className="text-sm text-gray-900">{new Date().toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Configuration Notes */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Configuration Notes</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Configuration is loaded from config.yaml file and environment variables</p>
          <p>• API keys and secrets are stored securely in environment variables</p>
          <p>• Changes to configuration require restart of the bot</p>
          <p>• Risk management settings can be adjusted via the config file</p>
        </div>
      </div>
    </div>
  )
}

export default Config 