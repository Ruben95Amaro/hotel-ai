import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { Loader2, Calendar, Users, CreditCard, CheckCircle, AlertCircle, ArrowLeft, Shield, Star } from 'lucide-react'
import { useForm } from 'react-hook-form'

const roomDetails = {
  standard: { name: 'Standard Room', price: 150, maxGuests: 2 },
  deluxe: { name: 'Deluxe Room', price: 250, maxGuests: 3 },
  suite: { name: 'Junior Suite', price: 400, maxGuests: 4 },
  presidential: { name: 'Presidential Suite', price: 800, maxGuests: 4 },
}

export default function Booking() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: details, 2: guest info, 3: payment, 4: confirmation
  const [bookingData, setBookingData] = useState(null)

  const roomId = searchParams.get('room') || 'standard'
  const checkIn = searchParams.get('checkIn')
  const checkOut = searchParams.get('checkOut')
  const guests = parseInt(searchParams.get('guests')) || 2

  const room = roomDetails[roomId] || roomDetails.standard
  const nights = checkIn && checkOut ? Math.ceil((new Date(checkOut) - new Date(checkIn)) / (1000 * 60 * 60 * 24)) : 1
  const subtotal = room.price * nights
  const taxes = subtotal * 0.13
  const total = subtotal + taxes

  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      specialRequests: '',
      cardNumber: '',
      cardExpiry: '',
      cardCvv: '',
      cardName: '',
    }
  })

  const onSubmit = async (data, stepNum) => {
    if (stepNum === 1) {
      // Validate dates and guests
      if (!checkIn || !checkOut) {
        alert('Please select check-in and check-out dates')
        return
      }
      if (guests > room.maxGuests) {
        alert(`Maximum ${room.maxGuests} guests for this room type`)
        return
      }
      setStep(2)
    } else if (stepNum === 2) {
      setStep(3)
    } else if (stepNum === 3) {
      setLoading(true)
      try {
        // Simulate booking creation
        await new Promise(resolve => setTimeout(resolve, 1500))
        const confirmationCode = 'GO' + Math.random().toString(36).substr(2, 6).toUpperCase()
        setBookingData({ ...data, confirmationCode, room: room.name, checkIn, checkOut, nights, guests, total })
        setStep(4)
      } catch (error) {
        alert('Booking failed. Please try again.')
      } finally {
        setLoading(false)
      }
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  }

  const steps = [
    { num: 1, label: 'Stay Details' },
    { num: 2, label: 'Guest Info' },
    { num: 3, label: 'Payment' },
    { num: 4, label: 'Confirmation' },
  ]

  if (step === 4 && bookingData) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 lg:py-16">
        <div className="container-custom">
          <div className="max-w-2xl mx-auto">
            {/* Success Animation */}
            <div className="text-center mb-8">
              <div className="w-24 h-24 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center animate-pulse">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
              <h1 className="font-display text-3xl font-medium text-gray-900 mb-2">Booking Confirmed!</h1>
              <p className="text-gray-600">Your reservation has been successfully created.</p>
            </div>

            {/* Confirmation Details */}
            <div className="card p-8 mb-8">
              <div className="flex items-center space-x-3 mb-6 p-4 bg-primary-50 rounded-lg">
                <Shield className="h-6 w-6 text-primary-600" />
                <div>
                  <div className="font-medium text-gray-900">Confirmation Code</div>
                  <div className="font-display text-2xl font-bold text-primary-600 tracking-wider">{bookingData.confirmationCode}</div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Room Type</span>
                  <span className="font-medium">{bookingData.room}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Check-in</span>
                  <span className="font-medium">{formatDate(bookingData.checkIn)}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Check-out</span>
                  <span className="font-medium">{formatDate(bookingData.checkOut)}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Nights</span>
                  <span className="font-medium">{bookingData.nights}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Guests</span>
                  <span className="font-medium">{bookingData.guests}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Guest Name</span>
                  <span className="font-medium">{bookingData.firstName} {bookingData.lastName}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Email</span>
                  <span className="font-medium">{bookingData.email}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-600">Total Paid</span>
                  <span className="font-display text-xl font-bold text-primary-600">€{bookingData.total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <button 
                onClick={() => navigate('/bookings')}
                className="btn-primary w-full py-3"
              >
                View My Bookings
              </button>
              <button 
                onClick={() => navigate('/rooms')}
                className="btn-secondary w-full py-3"
              >
                Continue Shopping
              </button>
            </div>

            <p className="text-center text-sm text-gray-500 mt-6">
              A confirmation email has been sent to <strong>{bookingData.email}</strong>
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 lg:py-12">
      <div className="container-custom">
        {/* Progress Steps */}
        <div className="mb-8 hidden md:flex">
          <div className="flex items-center">
            {steps.map((s, i) => (
              <React.Fragment key={s.num}>
                <div className="flex items-center space-x-2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                    step >= s.num ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {step > s.num ? <CheckCircle className="h-5 w-5" /> : s.num}
                  </div>
                  {i < steps.length - 1 && (
                    <div className={`w-16 h-0.5 mx-2 ${
                      step > s.num ? 'bg-primary-600' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
                <span className={`text-sm font-medium ml-2 mr-8 ${step >= s.num ? 'text-primary-600' : 'text-gray-500'}`}>
                  {s.label}
                </span>
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Mobile Step Indicator */}
        <div className="md:hidden mb-6 flex items-center justify-between">
          {steps.map((s) => (
            <div key={s.num} className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                step >= s.num ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'
              }`}>
                {step > s.num ? <CheckCircle className="h-5 w-5" /> : s.num}
              </div>
              <span className={`text-xs mt-1 ${step >= s.num ? 'text-primary-600' : 'text-gray-500'}`}>{s.label}</span>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Booking Summary */}
          <div className="lg:col-span-1">
            <div className="card p-6 sticky top-24">
              <h3 className="font-display text-lg font-medium text-gray-900 mb-4">Booking Summary</h3>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-center space-x-3 p-3 bg-primary-50 rounded-lg">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Star className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{room.name}</div>
                    <div className="text-sm text-gray-500">Max {room.maxGuests} guests</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 text-sm">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">{formatDate(checkIn)} - {formatDate(checkOut)}</div>
                    <div className="text-gray-500">{nights} night{nights > 1 ? 's' : ''}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 text-sm">
                  <Users className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">{guests} Guest{guests > 1 ? 's' : ''}</div>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-100 pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">{room.name} × {nights} night{nights > 1 ? 's' : ''}</span>
                  <span className="font-medium">€{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Taxes & Fees (13%)</span>
                  <span className="font-medium">€{taxes.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold pt-2 border-t border-gray-100">
                  <span>Total</span>
                  <span className="text-primary-600">€{total.toFixed(2)}</span>
                </div>
                <p className="text-xs text-gray-500 text-center">Price guaranteed in EUR</p>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="lg:col-span-2">
            <div className="card p-6 lg:p-8">
              {step === 1 && (
                <form onSubmit={handleSubmit((data) => onSubmit(data, 1))}>
                  <h3 className="font-display text-xl font-medium text-gray-900 mb-6">Stay Details</h3>
                  
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <label className="label">Check-in</label>
                      <div className="flex items-center bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
                        <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                        <span className="font-medium">{formatDate(checkIn)}</span>
                      </div>
                    </div>
                    <div>
                      <label className="label">Check-out</label>
                      <div className="flex items-center bg-gray-50 rounded-lg px-4 py-3 border border-gray-200">
                        <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                        <span className="font-medium">{formatDate(checkOut)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mb-6">
                    <label className="label">Guests</label>
                    <select 
                      {...register('guests', { required: true, valueAsNumber: true })}
                      defaultValue={guests}
                      className="input"
                    >
                      {[1, 2, 3, 4].filter(g => g <= room.maxGuests).map((g) => (
                        <option key={g} value={g}>{g} Guest{g > 1 ? 's' : ''}</option>
                      ))}
                    </select>
                    {errors.guests && <p className="text-red-500 text-sm mt-1">Required</p>}
                  </div>

                  <div className="mb-6">
                    <label className="label">Special Requests</label>
                    <textarea
                      {...register('specialRequests')}
                      rows={3}
                      className="input"
                      placeholder="Late check-in, dietary requirements, accessibility needs, etc."
                    />
                  </div>

                  <button type="submit" className="btn-primary w-full py-3" disabled={loading}>
                    {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Continue to Guest Info'}
                  </button>
                </form>
              )}

              {step === 2 && (
                <form onSubmit={handleSubmit((data) => onSubmit(data, 2))}>
                  <h3 className="font-display text-xl font-medium text-gray-900 mb-6">Guest Information</h3>
                  
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <label className="label">First Name *</label>
                      <input {...register('firstName', { required: true })} className="input" placeholder="John" />
                      {errors.firstName && <p className="text-red-500 text-sm mt-1">Required</p>}
                    </div>
                    <div>
                      <label className="label">Last Name *</label>
                      <input {...register('lastName', { required: true })} className="input" placeholder="Doe" />
                      {errors.lastName && <p className="text-red-500 text-sm mt-1">Required</p>}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <label className="label">Email *</label>
                      <input {...register('email', { required: true, pattern: /^\S+@\S+$/i })} type="email" className="input" placeholder="john@example.com" />
                      {errors.email && <p className="text-red-500 text-sm mt-1">Valid email required</p>}
                    </div>
                    <div>
                      <label className="label">Phone</label>
                      <input {...register('phone')} type="tel" className="input" placeholder="+351 XX XXX XXXX" />
                    </div>
                  </div>

                  <div className="mb-6">
                    <label className="label">Special Requests</label>
                    <textarea
                      {...register('specialRequests')}
                      rows={3}
                      className="input"
                      placeholder="Any special requirements for your stay..."
                    />
                  </div>

                  <div className="flex space-x-4">
                    <button type="button" onClick={() => setStep(1)} className="btn-secondary flex-1">Back</button>
                    <button type="submit" className="btn-primary flex-1 py-3" disabled={loading}>
                      {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Continue to Payment'}
                    </button>
                  </div>
                </form>
              )}

              {step === 3 && (
                <form onSubmit={handleSubmit((data) => onSubmit(data, 3))}>
                  <h3 className="font-display text-xl font-medium text-gray-900 mb-6">Payment Details</h3>
                  
                  <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Shield className="h-5 w-5 text-green-600" />
                      <div>
                        <div className="font-medium text-green-800">Secure Payment</div>
                        <div className="text-sm text-green-700">Your payment information is encrypted and processed securely. We never store your card details.</div>
                      </div>
                    </div>
                  </div>

                  <div className="mb-6">
                    <label className="label">Card Number *</label>
                    <input {...register('cardNumber', { required: true })} className="input" placeholder="4242 4242 4242 4242" maxLength={19} />
                    {errors.cardNumber && <p className="text-red-500 text-sm mt-1">Required</p>}
                  </div>

                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <label className="label">Expiry *</label>
                      <input {...register('cardExpiry', { required: true })} className="input" placeholder="MM/YY" maxLength={5} />
                      {errors.cardExpiry && <p className="text-red-500 text-sm mt-1">Required</p>}
                    </div>
                    <div>
                      <label className="label">CVV *</label>
                      <input {...register('cardCvv', { required: true })} type="password" className="input" placeholder="123" maxLength={4} />
                      {errors.cardCvv && <p className="text-red-500 text-sm mt-1">Required</p>}
                    </div>
                  </div>

                  <div className="mb-6">
                    <label className="label">Name on Card *</label>
                    <input {...register('cardName', { required: true })} className="input" placeholder="JOHN DOE" />
                    {errors.cardName && <p className="text-red-500 text-sm mt-1">Required</p>}
                  </div>

                  <div className="flex space-x-4">
                    <button type="button" onClick={() => setStep(2)} className="btn-secondary flex-1">Back</button>
                    <button type="submit" className="btn-primary flex-1 py-3" disabled={loading}>
                      {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : `Pay €${total.toFixed(2)}`}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}