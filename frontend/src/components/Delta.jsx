import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  RefreshCw, 
  XCircle,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Target
} from 'lucide-react'

function Delta() {
  const [delta, setDelta] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDelta = async () => {
    try {
      setLoading(true)
      const [deltaResponse, recommendationResponse] = await Promise.all([
        axios.get('/api/delta'),
        axios.get('/api/hedge-recommendation')
      ])
      
      setDelta(deltaResponse.data)
      setRecommendation(recommendationResponse.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch delta data')
      console.error('Error fetching delta:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDelta()
    
    // Refresh every 15 seconds
    const interval = setInterval(fetchDelta, 15000)
    return () => clearInterval(interval)
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
        <button onClick={fetchDelta} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }

  if (!delta || Object.keys(delta).length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No delta data available</p>
      </div>
    )
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high': return 'text-danger-600 bg-danger-100'
      case 'medium': return 'text-warning-600 bg-warning-100'
      case 'low': return 'text-success-600 bg-success-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getActionColor = (action) => {
    switch (action) {
      case 'buy': return 'text-success-600'
      case 'sell': return 'text-danger-600'
      case 'hold': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Delta Analysis</h2>
        <button 
          onClick={fetchDelta}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total LP Value */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DollarSign className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total LP Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${delta.total_lp_value?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        {/* Net Delta */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {delta.net_delta > 0 ? (
                <TrendingUp className="h-8 w-8 text-success-600" />
              ) : (
                <TrendingDown className="h-8 w-8 text-danger-600" />
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Net Delta</p>
              <p className={`text-2xl font-bold ${
                delta.net_delta > 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                ${delta.net_delta?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>
        </div>

        {/* Hedge Status */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {delta.hedge_needed ? (
                <AlertTriangle className="h-8 w-8 text-warning-600" />
              ) : (
                <CheckCircle className="h-8 w-8 text-success-600" />
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Hedge Status</p>
              <p className={`text-lg font-semibold ${
                delta.hedge_needed ? 'text-warning-600' : 'text-success-600'
              }`}>
                {delta.hedge_needed ? 'Needed' : 'Balanced'}
              </p>
            </div>
          </div>
        </div>

        {/* Confidence */}
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Target className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Confidence</p>
              <p className="text-2xl font-bold text-gray-900">
                {((delta.confidence || 0) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Delta Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Token Exposures */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Exposures</h3>
          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-600">Token 0</span>
                <span className={`text-sm font-bold ${
                  delta.token0_exposure > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  ${delta.token0_exposure?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    delta.token0_exposure > 0 ? 'bg-success-500' : 'bg-danger-500'
                  }`}
                  style={{ 
                    width: `${Math.min(Math.abs(delta.token0_exposure || 0) / (delta.total_lp_value || 1) * 100, 100)}%` 
                  }}
                ></div>
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-600">Token 1</span>
                <span className={`text-sm font-bold ${
                  delta.token1_exposure > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  ${delta.token1_exposure?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    delta.token1_exposure > 0 ? 'bg-success-500' : 'bg-danger-500'
                  }`}
                  style={{ 
                    width: `${Math.min(Math.abs(delta.token1_exposure || 0) / (delta.total_lp_value || 1) * 100, 100)}%` 
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Hedge Details */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hedge Details</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Hedge Token</p>
                <p className="text-lg font-semibold text-gray-900">{delta.hedge_token || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Hedge Amount</p>
                <p className="text-lg font-semibold text-gray-900">${delta.hedge_amount?.toFixed(2) || '0.00'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Direction</p>
                <p className="text-lg font-semibold text-gray-900 capitalize">{delta.hedge_direction || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Threshold</p>
                <p className="text-lg font-semibold text-gray-900">$50.00</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hedge Recommendation */}
      {recommendation && !recommendation.error && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hedge Recommendation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="border rounded-lg p-4">
              <p className="text-sm font-medium text-gray-500">Action</p>
              <p className={`text-lg font-semibold capitalize ${getActionColor(recommendation.action)}`}>
                {recommendation.action}
              </p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm font-medium text-gray-500">Amount</p>
              <p className="text-lg font-semibold text-gray-900">${recommendation.amount?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm font-medium text-gray-500">Token</p>
              <p className="text-lg font-semibold text-gray-900">{recommendation.token}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm font-medium text-gray-500">Urgency</p>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUrgencyColor(recommendation.urgency)}`}>
                {recommendation.urgency}
              </span>
            </div>
          </div>
          {recommendation.reason && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">{recommendation.reason}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Delta 