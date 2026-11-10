import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { Heart, Loader2, Plus, Send, X, CheckCircle, Clock, AlertCircle, Zap, MessageSquare, ChevronDown, ChevronUp, Utensils, Accessibility as Wheelchair, Sparkles, Car, FileText } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

const requestTypes = [
  { value: 'room_preference', label: 'Room Preference', icon: <Heart className="h-5 w-5" /> },
  { value: 'dietary', label: 'Dietary Requirements', icon: <Utensils className="h-5 w-5" /> },
  { value: 'accessibility', label: 'Accessibility Needs', icon: <Wheelchair className="h-5 w-5" /> },
  { value: 'celebration', label: 'Special Occasion', icon: <Sparkles className="h-5 w-5" /> },
  { value: 'transport', label: 'Transportation', icon: <Car className="h-5 w-5" /> },
  { value: 'other', label: 'Other Request', icon: <FileText className="h-5 w-5" /> },
]

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  confirmed: { label: 'Confirmed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  in_progress: { label: 'In Progress', color: 'bg-blue-100 text-blue-700', icon: Zap },
  completed: { label: 'Completed', color: 'bg-gray-100 text-gray-700', icon: CheckCircle },
  declined: { label: 'Declined', color: 'bg-red-100 text-red-700', icon: AlertCircle },
}

export default function Requests() {
  const { user, isAuthenticated } = useAuth()
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [expandedId, setExpandedId] = useState(null)
  const navigate = useNavigate()

  const { register, handleSubmit, reset, formState: { errors } } = useForm()

  useEffect(() => {
    if (isAuthenticated) {
      fetchRequests()
    }
  }, [isAuthenticated])

  const fetchRequests = async () => {
    try {
      setLoading(true)
      // const response = await hotelApi.getSpecialRequests()
      // setRequests(response.data)
      
      // Mock data
      setRequests([
        {
          id: '1',
          type: 'celebration',
          title: 'Anniversary Celebration',
          description: 'Surprise setup for 10th anniversary - rose petals, champagne, chocolate-covered strawberries',
          status: 'confirmed',
          created_at: '2025-01-15T10:00:00Z',
          updated_at: '2025-01-16T14:30:00Z',
        },
        {
          id: '2',
          type: 'dietary',
          title: 'Gluten-Free Meals',
          description: 'Guest has celiac disease - all meals must be gluten-free, separate preparation area',
          status: 'in_progress',
          created_at: '2025-01-20T09:00:00Z',
          updated_at: '2025-01-20T11:00:00Z',
        },
      ])
    } catch (error) {
      toast.error('Failed to load requests')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data) => {
    try {
      // await hotelApi.createSpecialRequest(data)
      await new Promise(resolve => setTimeout(resolve, 1000))
      const newRequest = {
        id: Date.now().toString(),
        ...data,
        status: 'pending',
        created_at: new Date().toISOString(),
      }
      setRequests([newRequest, ...requests])
      toast.success('Special request submitted successfully')
      setShowModal(false)
      reset()
    } catch (error) {
      toast.error('Failed to submit request')
    }
  }

  const getTypeInfo = (type) => {
    return requestTypes.find(t => t.value === type) || { label: type, icon: '📝' }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
        <div className="container-custom text-center">
          <div className="card p-12 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
              <Heart className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">Sign in for Special Requests</h2>
            <p className="text-gray-600 mb-6">Submit and track special requests for your stay.</p>
            <div className="flex space-x-3">
              <button onClick={() => navigate('/login')} className="btn-primary flex-1">Sign In</button>
              <button onClick={() => navigate('/register')} className="btn-secondary flex-1">Sign Up</button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 lg:py-12">
      <div className="container-custom">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-3xl lg:text-4xl font-medium text-gray-900">Special Requests</h1>
            <p className="text-gray-600 mt-1">Make your stay perfect with personalized requests</p>
          </div>
          <button onClick={() => { reset(); setShowModal(true); }} className="btn-primary flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>New Request</span>
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        ) : requests.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <Heart className="h-8 w-8 text-gray-400" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">No Special Requests</h2>
            <p className="text-gray-600 mb-6">Submit your first request to make your stay truly personalized.</p>
            <button onClick={() => { reset(); setShowModal(true); }} className="btn-primary">
              Create Request
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {requests.map((request) => {
              const config = statusConfig[request.status] || statusConfig.pending
              const Icon = config.icon
              const typeInfo = getTypeInfo(request.type)

              return (
                <div key={request.id} className="card overflow-hidden">
                  <div className="p-6 lg:p-8">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-2xl">
                          {typeInfo.icon}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-display text-lg font-medium text-gray-900">{request.title}</h3>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
                              <Icon className="h-3 w-3 inline mr-1" />
                              {config.label}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mt-1">{typeInfo.label} • Submitted {new Date(request.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                    </div>

                    <p className="text-gray-600 mb-4">{request.description}</p>

                    <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-100">
                      <span>Last updated: {new Date(request.updated_at).toLocaleDateString()}</span>
                      <button
                        onClick={() => setExpandedId(expandedId === request.id ? null : request.id)}
                        className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
                      >
                        <span>{expandedId === request.id ? 'Hide timeline' : 'Show timeline'}</span>
                        {expandedId === request.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  {expandedId === request.id && (
                    <div className="bg-gray-50 px-6 lg:px-8 pb-6 lg:pb-8 border-t border-gray-100 animate-slide-down">
                      <h4 className="font-medium text-gray-900 mb-4">Status Timeline</h4>
                      <div className="relative pl-4 border-l-2 border-gray-200">
                        {[
                          { status: 'pending', label: 'Submitted', time: request.created_at, completed: true },
                          { status: 'confirmed', label: 'Confirmed by Team', time: request.updated_at, completed: ['confirmed', 'in_progress', 'completed', 'declined'].includes(request.status) },
                          { status: 'in_progress', label: 'In Progress', time: null, completed: ['in_progress', 'completed'].includes(request.status) },
                          { status: 'completed', label: 'Completed', time: null, completed: request.status === 'completed' },
                        ].map((step, idx) => (
                          <div key={step.status} className="relative mb-6">
                            <div className="absolute left-[-28px] top-0 w-5 h-5 rounded-full border-2 flex items-center justify-center bg-white z-10"
                              style={{ borderColor: step.completed ? '#10b981' : '#e5e7eb' }}>
                              {step.completed && <CheckCircle className="h-3 w-3 text-white" style={{ background: 'none' }} />}
                            </div>
                            <div className="ml-4">
                              <div className="font-medium text-gray-900">{step.label}</div>
                              {step.time && <div className="text-sm text-gray-500">{new Date(step.time).toLocaleString()}</div>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* New Request Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div className="bg-white rounded-2xl p-6 lg:p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-display text-xl font-medium text-gray-900">New Special Request</h3>
                <button onClick={() => setShowModal(false)} className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                  <X className="h-6 w-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div>
                  <label className="label">Request Type</label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {requestTypes.map((type) => (
                      <label key={type.value} className="relative cursor-pointer">
                        <input
                          type="radio"
                          {...register('type', { required: true })}
                          value={type.value}
                          className="sr-only peer"
                        />
                        <div className={`p-4 rounded-xl border-2 transition-all text-center ${
                          'peer-checked:border-primary-500 peer-checked:bg-primary-50 border-gray-200'
                        }`}>
                          <div className="text-2xl mb-1">{type.icon}</div>
                          <div className="text-sm font-medium text-gray-700">{type.label}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                  {errors.type && <p className="text-red-500 text-sm mt-1">Please select a type</p>}
                </div>

                <div>
                  <label className="label">Title *</label>
                  <input {...register('title', { required: true })} className="input" placeholder="e.g., Anniversary Surprise Setup" />
                  {errors.title && <p className="text-red-500 text-sm mt-1">Required</p>}
                </div>

                <div>
                  <label className="label">Description *</label>
                  <textarea {...register('description', { required: true })} rows={4} className="input" placeholder="Please provide details about your request..." />
                  {errors.description && <p className="text-red-500 text-sm mt-1">Required</p>}
                </div>

                <div className="flex space-x-3 pt-4 border-t border-gray-100">
                  <button type="button" onClick={() => setShowModal(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" className="btn-primary flex-1">
                    <Send className="h-5 w-5 mr-2" />
                    Submit Request
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}