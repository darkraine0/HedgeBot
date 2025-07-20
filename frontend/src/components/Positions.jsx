import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  RefreshCw, 
  XCircle,
  CheckCircle,
  X,
  TrendingUp,
  TrendingDown
} from 'lucide-react'

function Positions() {
  const [positions, setPositions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchPositions = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/positions')
      setPositions(response.data.positions || [])
      setError(null)
    } catch (err) {
      setError('Failed to fetch positions')
      console.error('Error fetching positions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPositions()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchPositions, 30000)
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
        <button onClick={fetchPositions} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">LP Positions</h2>
        <button 
          onClick={fetchPositions}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Summary */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Total Positions</p>
            <p className="text-2xl font-bold text-gray-900">{positions.length}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Value</p>
            <p className="text-2xl font-bold text-gray-900">
              ${positions.reduce((sum, pos) => sum + (pos.total_usd_value || 0), 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">In Range</p>
            <p className="text-2xl font-bold text-gray-900">
              {positions.filter(pos => pos.in_range).length} / {positions.length}
            </p>
          </div>
        </div>
      </div>

      {/* Positions List */}
      {positions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No positions found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {positions.map((position) => (
            <div key={position.nft_id} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Position #{position.nft_id}
                  </h3>
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
                    position.in_range 
                      ? 'bg-success-100 text-success-800' 
                      : 'bg-warning-100 text-warning-800'
                  }`}>
                    {position.in_range ? (
                      <CheckCircle className="h-3 w-3" />
                    ) : (
                      <X className="h-3 w-3" />
                    )}
                    <span>{position.in_range ? 'In Range' : 'Out of Range'}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-500">Total Value</p>
                  <p className="text-lg font-bold text-gray-900">
                    ${position.total_usd_value?.toLocaleString() || '0'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Token 0 */}
                <div className="border rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Token 0</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Symbol:</span>
                      <span className="text-sm font-medium">{position.token0.symbol}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Balance:</span>
                      <span className="text-sm font-medium">{position.token0.balance?.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Price:</span>
                      <span className="text-sm font-medium">${position.token0.price_usd?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">USD Value:</span>
                      <span className="text-sm font-medium">${position.token0.usd_value?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Uncollected Fees:</span>
                      <span className="text-sm font-medium">{position.uncollected_fees_token0?.toFixed(6)}</span>
                    </div>
                  </div>
                </div>

                {/* Token 1 */}
                <div className="border rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Token 1</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Symbol:</span>
                      <span className="text-sm font-medium">{position.token1.symbol}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Balance:</span>
                      <span className="text-sm font-medium">{position.token1.balance?.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Price:</span>
                      <span className="text-sm font-medium">${position.token1.price_usd?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">USD Value:</span>
                      <span className="text-sm font-medium">${position.token1.usd_value?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Uncollected Fees:</span>
                      <span className="text-sm font-medium">{position.uncollected_fees_token1?.toFixed(6)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Position Details */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Pool Address</p>
                    <p className="text-sm text-gray-900 font-mono">{position.pool_address}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Fee Tier</p>
                    <p className="text-sm text-gray-900">{position.fee_tier} bps</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Liquidity</p>
                    <p className="text-sm text-gray-900">{position.liquidity?.toLocaleString()}</p>
                  </div>
                </div>
                
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Tick Range</p>
                    <p className="text-sm text-gray-900">
                      {position.tick_lower} to {position.tick_upper}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Current Tick</p>
                    <p className="text-sm text-gray-900">{position.current_tick || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Positions 