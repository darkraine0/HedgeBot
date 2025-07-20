import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  DollarSign,
  Activity,
  Shield,
  Zap,
  BarChart3,
  Clock
} from 'lucide-react'

function Dashboard() {
  const [state, setState] = useState(null)
  const [marketData, setMarketData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      const [stateResponse, marketResponse] = await Promise.all([
        axios.get('/api/state'),
        axios.get('/api/market-data')
      ])
      
      setState(stateResponse.data)
      setMarketData(marketResponse.data)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <span className="ml-2 text-red-800">{error}</span>
        </div>
      </div>
    )
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatDelta = (delta) => {
    if (!delta) return '$0'
    const formatted = formatCurrency(Math.abs(delta))
    return delta >= 0 ? `+${formatted}` : `-${formatted}`
  }

  const getDeltaColor = (delta) => {
    if (!delta) return 'text-gray-500'
    return delta >= 0 ? 'text-success-600' : 'text-danger-600'
  }

  const getDeltaIcon = (delta) => {
    if (!delta) return TrendingUp
    return delta >= 0 ? TrendingUp : TrendingDown
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring of your LP positions and hedging status</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>Live updates every 10s</span>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total LP Value */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total LP Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {state?.total_lp_value ? formatCurrency(state.total_lp_value) : '$0'}
              </p>
            </div>
          </div>
        </div>

        {/* Net Delta */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Net Delta</p>
              <div className="flex items-center">
                {state?.current_delta ? (
                  <>
                    {React.createElement(getDeltaIcon(state.current_delta.net_delta), {
                      className: `h-5 w-5 ${getDeltaColor(state.current_delta.net_delta)}`
                    })}
                    <p className={`ml-2 text-2xl font-bold ${getDeltaColor(state.current_delta.net_delta)}`}>
                      {formatDelta(state.current_delta.net_delta)}
                    </p>
                  </>
                ) : (
                  <p className="text-2xl font-bold text-gray-400">$0</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Position Count */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Positions</p>
              <p className="text-2xl font-bold text-gray-900">
                {state?.position_count || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Bot Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${
              state?.running ? 'bg-green-100' : 'bg-red-100'
            }`}>
              <Shield className={`h-6 w-6 ${
                state?.running ? 'text-green-600' : 'text-red-600'
              }`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Bot Status</p>
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  state?.running ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <p className="text-lg font-semibold text-gray-900">
                  {state?.running ? 'Running' : 'Stopped'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Market Data */}
      {marketData && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Market Overview</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">In Range</p>
                <p className="text-lg font-semibold text-green-600">
                  {marketData.in_range_positions || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Out of Range</p>
                <p className="text-lg font-semibold text-orange-600">
                  {marketData.out_of_range_positions || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-lg font-semibold text-gray-900">
                  {formatCurrency(marketData.total_value || 0)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Update</p>
                <p className="text-sm text-gray-500">
                  {marketData.timestamp ? new Date(marketData.timestamp).toLocaleTimeString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hedge Recommendation */}
      {state?.current_delta?.hedge_needed && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-6 w-6 text-yellow-600" />
            <div className="ml-3">
              <h3 className="text-lg font-medium text-yellow-800">Hedge Recommendation</h3>
              <p className="text-yellow-700">
                Net delta of {formatDelta(state.current_delta.net_delta)} exceeds threshold. 
                Consider hedging {state.current_delta.hedge_token} position.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Task Status */}
      {state?.task_status && Object.keys(state.task_status).length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Task Status</h3>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {Object.entries(state.task_status).map(([taskName, task]) => (
                <div key={taskName} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-3 ${
                      task.running ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                    <span className="font-medium text-gray-900 capitalize">
                      {taskName.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Last: {new Date(task.last_run * 1000).toLocaleTimeString()}</span>
                    {task.error_count > 0 && (
                      <span className="text-red-600">Errors: {task.error_count}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard 