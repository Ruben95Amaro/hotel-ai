import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { User, Mail, Phone, MapPin, Calendar, Loader2, Save, AlertCircle, CheckCircle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, isAuthenticated } = useAuth()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      documentId: '',
      nationality: '',
    }
  })

  useEffect(() => {
    if (isAuthenticated && user) {
      reset({
        firstName: user.full_name?.split(' ')[0] || '',
        lastName: user.full_name?.split(' ').slice(1).join(' ') || '',
        email: user.email || '',
        phone: user.phone || '',
        documentId: user.document_id || '',
        nationality: user.nationality || '',
      })
    }
  }, [user, isAuthenticated, reset])

  const onSubmit = async (data) => {
    try {
      setSaving(true)
      // await hotelApi.updateProfile(data)
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Profile updated successfully')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
        <div className="container-custom text-center">
          <div className="card p-12 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="h-8 w-8 text-primary-600" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">Sign in to View Profile</h2>
            <p className="text-gray-600 mb-6">Manage your personal information and preferences.</p>
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
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl lg:text-4xl font-medium text-gray-900">My Profile</h1>
            <p className="text-gray-600 mt-1">Manage your personal information and preferences</p>
          </div>

          {/* Profile Card */}
          <div className="card p-6 lg:p-8 mb-8">
            <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 mb-8">
              <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="h-12 w-12 text-primary-600" />
              </div>
              <div className="text-center sm:text-left">
                <h2 className="font-display text-2xl font-medium text-gray-900">{user?.full_name || 'Guest'}</h2>
                <p className="text-gray-500 mt-1">{user?.email}</p>
                <p className="text-xs text-gray-400 mt-2">Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '2024'}</p>
              </div>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="label">First Name *</label>
                  <input {...register('firstName', { required: true })} className="input" />
                  {errors.firstName && <p className="text-red-500 text-sm mt-1">Required</p>}
                </div>
                <div>
                  <label className="label">Last Name *</label>
                  <input {...register('lastName', { required: true })} className="input" />
                  {errors.lastName && <p className="text-red-500 text-sm mt-1">Required</p>}
                </div>
              </div>

              <div>
                <label className="label">Email *</label>
                <input {...register('email', { required: true, pattern: /^\S+@\S+$/i })} type="email" className="input" />
                {errors.email && <p className="text-red-500 text-sm mt-1">Valid email required</p>}
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="label">Phone</label>
                  <input {...register('phone')} type="tel" className="input" placeholder="+351 XX XXX XXXX" />
                </div>
                <div>
                  <label className="label">Document ID</label>
                  <input {...register('documentId')} className="input" placeholder="Passport/ID Number" />
                </div>
              </div>

              <div>
                <label className="label">Nationality</label>
                <input {...register('nationality')} className="input" placeholder="Portuguese" />
              </div>

              <div className="pt-4 border-t border-gray-100">
                <button type="submit" disabled={saving} className="btn-primary w-full sm:w-auto py-3">
                  {saving ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <Save className="h-5 w-5 mr-2" />} Save Changes
                </button>
              </div>
            </form>
          </div>

          {/* Preferences */}
          <div className="card p-6 lg:p-8 mb-8">
            <h3 className="font-display text-lg font-medium text-gray-900 mb-6">Preferences</h3>
            <div className="space-y-4">
              {[
                { key: 'roomType', label: 'Preferred Room Type', options: ['Standard', 'Deluxe', 'Suite', 'Presidential'] },
                { key: 'floor', label: 'Preferred Floor', options: ['Low (1-3)', 'Mid (4-6)', 'High (7+)', 'No Preference'] },
                { key: 'bed', label: 'Bed Preference', options: ['King', 'Twin', 'No Preference'] },
                { key: 'dietary', label: 'Dietary Requirements', options: ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Halal', 'Kosher', 'Other'] },
              ].map((pref) => (
                <div key={pref.key} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                  <label className="font-medium text-gray-700">{pref.label}</label>
                  <select className="px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                    {pref.options.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Account Actions */}
          <div className="card p-6 lg:p-8 border border-red-200 bg-red-50">
            <h3 className="font-display text-lg font-medium text-red-900 mb-4">Danger Zone</h3>
            <p className="text-red-700 mb-6">Once you delete your account, there is no going back. Please be certain.</p>
            <button className="btn bg-red-600 text-white hover:bg-red-700">
              <AlertCircle className="h-5 w-5 mr-2" />
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}