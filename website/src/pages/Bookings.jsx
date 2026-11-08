import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { Calendar, Users, Star, XCircle, Loader2, AlertCircle, CheckCircle, Clock, ChevronDown, ChevronUp, MessageSquare, Heart, Zap } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

const statusConfig = {
  confirmed: { label: 'Confirmed', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  checked_in: { label: 'Checked In', color: 'bg-blue-100 text-blue-700', icon: Zap },
  checked_out: { label: 'Completed', color: 'bg-gray-100 text-gray-700', icon: CheckCircle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: XCircle },
  no_show: { label: 'No Show', color: 'bg-red-100 text-red-700', icon: AlertCircle },
}

const roomIcons = {
  standard: '🏠',
  deluxe: '🏨',
  suite: '🏰',
  presidential: '👑',
}

export default function Bookings() {
  const { user, isAuthenticated } = useAuth()
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [cancellingId, setCancellingId] = useState(null)
  const [cancelReason, setCancelReason] = useState('')
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [expandedId, setExpandedId] = useState(null)

  const { register, handleSubmit, reset } = useForm()

  useEffect(() => {
    if (isAuthenticated) {
      fetchBookings()
    }
  }, [isAuthenticated])

  const fetchBookings = async () => {
    try {
      setLoading(true)
      // const response = await hotelApi.getBookings()
      // setBookings(response.data)
      
      // Mock data for demo
      setBookings([
        {
          id: '1',
          confirmation_code: 'GOA1B2C3',
          room_type: 'suite',
          check_in: '2025-02-15',
          check_out: '2025-02-18',
          guests: 2,
          nights: 3,
          total_price: 1200,
          status: 'confirmed',
          special_requests: 'Late check-in after 10pm',
          created_at: '2025-01-10T14:30:00Z',
        },
        {
          id: '2',
          confirmation_code: 'GOX9Y8Z7',
          room_type: 'deluxe',
          check_in: '2024-12-20',
          check_out: '2024-12-25',
          guests: 3,
          nights: 5,
          total_price: 1250,
          status: 'checked_out',
          special_requests: '',
          created_at: '2024-11-15T10:00:00Z',
        },
      ])
    } catch (error) {
      toast.error('Failed to load bookings')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatDateTime = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const handleCancel = async (bookingId) => {
    try {
      setCancellingId(bookingId)
      // await hotelApi.cancelBooking(bookingId, cancelReason)
      await new Promise(resolve => setTimeout(resolve, 1000))
      setBookings(bookings.map(b => b.id === bookingId ? { ...b, status: 'cancelled' } : b))
      toast.success('Booking cancelled successfully')
      setShowCancelModal(false)
      setCancelReason('')
    } catch (error) {
      toast.error('Failed to cancel booking')
    } finally {
      setCancellingId(null)
    }
  }

  const handleChat = (booking) => {
    // Navigate to chat with booking context
    window.location.href = `/chat?booking=${booking.confirmation_code}`
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
        <div className="container-custom text-center">
          <div className="card p-12 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
              <Calendar className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">Sign in to View Bookings</h2>
            <p className="text-gray-600 mb-6">Access your reservations, make changes, and contact our team.</p>
            <div className="flex space-x-3">
              <button onClick={() => window.location.href = '/login'} className="btn-primary flex-1">Sign In</button>
              <button onClick={() => window.location.href = '/register'} className="btn-secondary flex-1">Sign Up</button>
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
        <div className="mb-8">
          <h1 className="font-display text-3xl lg:text-4xl font-medium text-gray-900">My Bookings</h1>
          <p className="text-gray-600 mt-1">Manage your reservations and upcoming stays</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          </div>
        ) : bookings.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <Calendar className="h-8 w-8 text-gray-400" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">No Bookings Yet</h2>
            <p className="text-gray-600 mb-6">Your upcoming and past reservations will appear here.</p>
            <button onClick={() => window.location.href = '/rooms'} className="btn-primary">
              Book Your First Stay
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {bookings.map((booking) => {
              const config = statusConfig[booking.status] || statusConfig.pending
              const Icon = config.icon
              const isUpcoming = new Date(booking.check_in) > new Date()
              const isActive = booking.status === 'checked_in'
              const canCancel = isUpcoming && ['confirmed', 'pending'].includes(booking.status)

              return (
                <div key={booking.id} className="card overflow-hidden">
                  <div className="p-6 lg:p-8">
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-primary-100 rounded-xl flex items-center justify-center text-3xl">
                          {roomIcons[booking.room_type] || '🏨'}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-display text-xl font-medium text-gray-900">
                              {booking.room_type.charAt(0).toUpperCase() + booking.room_type.slice(1)} Room
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
                              <Icon className="h-3 w-3 inline mr-1" />
                              {config.label}
                            </span>
                          </div>
                          <p className="text-primary-600 font-medium mt-1">Confirmation: {booking.confirmation_code}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 lg:ml-auto">
                        {canCancel && (
                          <button
                            onClick={() => { setShowCancelModal(true); }}
                            className="btn-secondary text-sm"
                          >
                            Cancel
                          </button>
                        )}
                        <button
                          onClick={() => handleChat(booking)}
                          className="btn-accent text-sm flex items-center space-x-2"
                        >
                          <MessageSquare className="h-4 w-4" />
                          <span>AI Assistant</span>
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Calendar className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Check-in</div>
                          <div className="font-medium">{formatDate(booking.check_in)}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Calendar className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Check-out</div>
                          <div className="font-medium">{formatDate(booking.check_out)}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Users className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Guests</div>
                          <div className="font-medium">{booking.guests}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <Star className="h-5 w-5 text-primary-500" />
                        <div>
                          <div className="text-xs text-gray-500">Total</div>
                          <div className="font-medium text-primary-600">€{booking.total_price.toFixed(2)}</div>
                        </div>
                      </div>
                    </div>

                    {booking.special_requests && (
                      <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg mb-4">
                        <div className="flex items-center space-x-2 text-amber-800">
                          <Heart className="h-4 w-4" />
                          <span className="font-medium">Special Request:</span>
                          <span className="text-amber-700">{booking.special_requests}</span>
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-100">
                      <span>Booked on {formatDateTime(booking.created_at)}</span>
                      <button
                        onClick={() => setExpandedId(expandedId === booking.id ? null : booking.id)}
                        className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
                      >
                        <span>{expandedId === booking.id ? 'Hide details' : 'Show details'}</span>
                        {expandedId === booking.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  {expandedId === booking.id && (
                    <div className="bg-gray-50 px-6 lg:px-8 pb-6 lg:pb-8 border-t border-gray-100 animate-slide-down">
                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">Stay Details</h4>
                          <dl className="space-y-2 text-sm">
                            <div className="flex justify-between"><dt className="text-gray-500">Nights:</dt><dd className="font-medium">{booking.nights}</dd></div>
                            <div className="flex justify-between"><dt className="text-gray-500">Room Type:</dt><dd className="font-medium">{booking.room_type}</dd></div>
                            <div className="flex justify-between"><dt className="text-gray-500">Guests:</dt><dd className="font-medium">{booking.guests}</dd></div>
                            <div className="flex justify-between"><dt className="text-gray-500">Status:</dt><dd className="font-medium capitalize">{booking.status.replace('_', ' ')}</dd></div>
                          </dl>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">Pricing</h4>
                          <dl className="space-y-2 text-sm">
                            <div className="flex justify-between"><dt className="text-gray-500">Room Rate:</dt><dd className="font-medium">€{(booking.total_price / booking.nights).toFixed(2)}/night</dd></div>
                            <div className="flex justify-between"><dt className="text-gray-500">Subtotal:</dt><dd className="font-medium">€{(booking.total_price / 1.13).toFixed(2)}</dd></div>
                            <div className="flex justify-between"><dt className="text-gray-500">Taxes (13%):</dt><dd className="font-medium">€{(booking.total_price * 0.13 / 1.13).toFixed(2)}</dd></div>
                            <div className="flex justify-between border-t border-gray-200 pt-2"><dt className="text-gray-500">Total:</dt><dd className="font-bold text-primary-600">€{booking.total_price.toFixed(2)}</dd></div>
                          </dl>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Cancel Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div className="bg-white rounded-2xl p-6 lg:p-8 max-w-md w-full animate-slide-up">
              <h3 className="font-display text-xl font-medium text-gray-900 mb-4">Cancel Booking</h3>
              <p className="text-gray-600 mb-6">Please provide a reason for cancellation. This helps us improve our service.</p>
              <form onSubmit={handleSubmit((data) => handleCancel(cancellingId))}>
                <div className="mb-4">
                  <label className="label">Reason for Cancellation</label>
                  <textarea
                    {...register('cancelReason', { required: true })}
                    rows={3}
                    className="input"
                    placeholder="e.g., Change of plans, found better rate, emergency..."
                  />
                </div>
                <div className="flex space-x-3">
                  <button type="button" onClick={() => { setShowCancelModal(false); setCancelReason(''); }} className="btn-secondary flex-1">Keep Booking</button>
                  <button type="submit" disabled={cancellingId} className="btn bg-red-600 text-white hover:bg-red-700 flex-1">
                    {cancellingId ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : 'Confirm Cancellation'}
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