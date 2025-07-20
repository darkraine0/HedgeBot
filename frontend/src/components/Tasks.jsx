import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  RefreshCw, 
  XCircle,
  CheckCircle,
  AlertTriangle,
  Clock,
  Activity
} from 'lucide-react'

function Tasks() {
  const [tasks, setTasks] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/tasks')
      setTasks(response.data || {})
      setError(null)
    } catch (err) {
      setError('Failed to fetch task status')
      console.error('Error fetching tasks:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchTasks, 10000)
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
        <button onClick={fetchTasks} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never'
    const date = new Date(timestamp * 1000)
    return date.toLocaleTimeString()
  }

  const getStatusColor = (running) => {
    return running ? 'text-success-600' : 'text-gray-400'
  }

  const getStatusIcon = (running) => {
    return running ? CheckCircle : AlertTriangle
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Task Monitoring</h2>
        <button 
          onClick={fetchTasks}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Task Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Total Tasks</p>
            <p className="text-2xl font-bold text-gray-900">{Object.keys(tasks).length}</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Running</p>
            <p className="text-2xl font-bold text-success-600">
              {Object.values(tasks).filter(task => task.running).length}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Total Errors</p>
            <p className="text-2xl font-bold text-danger-600">
              {Object.values(tasks).reduce((sum, task) => sum + (task.error_count || 0), 0)}
            </p>
          </div>
        </div>
      </div>

      {/* Task Details */}
      {Object.keys(tasks).length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No tasks found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(tasks).map(([taskName, task]) => {
            const StatusIcon = getStatusIcon(task.running)
            return (
              <div key={taskName} className="card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <StatusIcon className={`h-6 w-6 ${getStatusColor(task.running)}`} />
                    <h4 className="text-lg font-semibold text-gray-900">{task.name}</h4>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    task.running 
                      ? 'bg-success-100 text-success-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {task.running ? 'Running' : 'Stopped'}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Interval</p>
                      <p className="text-sm text-gray-900">{task.interval}s</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Errors</p>
                      <p className={`text-sm font-medium ${
                        task.error_count > 0 ? 'text-danger-600' : 'text-gray-900'
                      }`}>
                        {task.error_count}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Last Run</p>
                      <p className="text-sm text-gray-900">{formatTime(task.last_run)}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Success Count</p>
                      <p className="text-sm text-gray-900">{task.success_count || 0}</p>
                    </div>
                  </div>

                  {task.avg_duration > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-500">Avg Duration</p>
                      <p className="text-sm text-gray-900">{task.avg_duration.toFixed(2)}s</p>
                    </div>
                  )}

                  {task.last_error && (
                    <div className="mt-3 p-3 bg-danger-50 border border-danger-200 rounded-lg">
                      <p className="text-sm font-medium text-danger-800 mb-1">Last Error</p>
                      <p className="text-sm text-danger-700">{task.last_error}</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* System Health */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Task Performance</h4>
            <div className="space-y-2">
              {Object.entries(tasks).map(([taskName, task]) => (
                <div key={taskName} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{task.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      task.running ? 'bg-success-500' : 'bg-gray-300'
                    }`} />
                    <span className="text-xs text-gray-500">
                      {task.error_count > 0 ? `${task.error_count} errors` : 'Healthy'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Recent Activity</h4>
            <div className="space-y-2">
              {Object.entries(tasks)
                .sort((a, b) => b[1].last_run - a[1].last_run)
                .slice(0, 3)
                .map(([taskName, task]) => (
                  <div key={taskName} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{task.name}</span>
                    <span className="text-xs text-gray-500">{formatTime(task.last_run)}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Tasks 