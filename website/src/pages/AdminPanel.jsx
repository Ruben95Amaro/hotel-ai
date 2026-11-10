import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { hotelApi } from '../services/api'
import { Users, Shield, Plus, Trash2, Loader2, AlertCircle, CheckCircle, Eye, EyeOff, Mail, Lock, User, Settings, BarChart3, Calendar, Bell, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AdminPanel() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('users')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    phone: '',
    isAdmin: false,
  })

  useEffect(() => {
    if (!isAuthenticated || !user?.is_admin) {
      navigate('/')
      return
    }
    fetchUsers()
  }, [isAuthenticated, user])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const response = await hotelApi.get('/auth/admin/users?limit=100')
      setUsers(response.data.users || [])
    } catch (error) {
      toast.error('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    if (!formData.email || !formData.password || !formData.firstName || !formData.lastName) {
      toast.error('Please fill all required fields')
      return
    }
    try {
      setCreating(true)
      await hotelApi.post('/auth/register', {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone: formData.phone,
      })
      
      if (formData.isAdmin) {
        // Make admin after creation
        const loginResponse = await hotelApi.post('/auth/login', {
          email: formData.email,
          password: formData.password,
        })
        const newUser = loginResponse.data.user
        await hotelApi.post(`/auth/admin/users/${newUser.id}/make-admin`)
      }
      
      toast.success('User created successfully')
      setShowCreateModal(false)
      setFormData({ email: '', password: '', firstName: '', lastName: '', phone: '', isAdmin: false })
      fetchUsers()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user')
    } finally {
      setCreating(false)
    }
  }

  const handleMakeAdmin = async (userId) => {
    try {
      await hotelApi.post(`/auth/admin/users/${userId}/make-admin`)
      toast.success('User promoted to admin')
      fetchUsers()
    } catch (error) {
      toast.error('Failed to promote user')
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return
    try {
      await hotelApi.delete(`/auth/admin/users/${userId}`)
      toast.success('User deleted')
      fetchUsers()
    } catch (error) {
      toast.error('Failed to delete user')
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (!isAuthenticated || !user?.is_admin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12">
        <div className="container-custom text-center">
          <div className="card p-12 max-w-md mx-auto">
            <div className="w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="font-display text-2xl font-medium text-gray-900 mb-3">Admin Access Required</h2>
            <p className="text-gray-600 mb-6">You don't have permission to access the admin panel.</p>
            <button onClick={() => navigate('/')} className="btn-primary">Go Home</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <nav className="container-custom" aria-label="Admin navigation">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="font-display text-xl font-semibold text-gray-900">Admin Panel</span>
              <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full">Grand Ocean Hotel</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Welcome, {user.full_name}</span>
              <button onClick={logout} className="btn-secondary text-sm flex items-center space-x-2">
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </nav>
      </header>

      <main className="container-custom py-8">
        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-8 border-b border-gray-200">
            {[
              { id: 'users', label: 'User Management', icon: Users },
              { id: 'bookings', label: 'All Bookings', icon: Calendar },
              { id: 'requests', label: 'Special Requests', icon: Bell },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="card">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <h3 className="font-display text-lg font-medium text-gray-900">User Management</h3>
              <button onClick={() => setShowCreateModal(true)} className="btn-primary flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                <span>Add User</span>
              </button>
            </div>
            
            {loading ? (
              <div className="p-8 text-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600 mx-auto" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-3 px-6 font-medium text-gray-500 text-sm">User</th>
                      <th className="text-left py-3 px-6 font-medium text-gray-500 text-sm">Email</th>
                      <th className="text-left py-3 px-6 font-medium text-gray-500 text-sm">Role</th>
                      <th className="text-left py-3 px-6 font-medium text-gray-500 text-sm">Status</th>
                      <th className="text-left py-3 px-6 font-medium text-gray-500 text-sm">Created</th>
                      <th className="text-right py-3 px-6 font-medium text-gray-500 text-sm">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-b border-gray-50 hover:bg-gray-50">
                        <td className="py-4 px-6">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                              <User className="h-5 w-5 text-primary-600" />
                            </div>
                            <span className="font-medium text-gray-900">{u.full_name}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6 text-gray-600">{u.email}</td>
                        <td className="py-4 px-6">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            u.is_admin ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'
                          }`}>
                            {u.is_admin ? 'Admin' : 'User'}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                            Active
                          </span>
                        </td>
                        <td className="py-4 px-6 text-gray-500 text-sm">{formatDate(u.created_at)}</td>
                        <td className="py-4 px-6 text-right">
                          <div className="flex items-center justify-end space-x-2">
                            {!u.is_admin && (
                              <button
                                onClick={() => handleMakeAdmin(u.id)}
                                className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                              >
                                Make Admin
                              </button>
                            )}
                            {u.id !== user.id && (
                              <button
                                onClick={() => handleDeleteUser(u.id)}
                                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                              >
                                Delete
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Other tabs placeholder */}
        {activeTab === 'bookings' && (
          <div className="card p-8 text-center">
            <Calendar className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="font-display text-lg font-medium text-gray-900 mb-2">All Bookings</h3>
            <p className="text-gray-500">Manage all hotel bookings from here.</p>
          </div>
        )}
        {activeTab === 'requests' && (
          <div className="card p-8 text-center">
            <Bell className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="font-display text-lg font-medium text-gray-900 mb-2">Special Requests</h3>
            <p className="text-gray-500">View and manage guest special requests.</p>
          </div>
        )}
        {activeTab === 'analytics' && (
          <div className="card p-8 text-center">
            <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <h3 className="font-display text-lg font-medium text-gray-900 mb-2">Analytics</h3>
            <p className="text-gray-500">Hotel performance metrics and reports.</p>
          </div>
        )}

        {/* Create User Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div className="bg-white rounded-2xl p-6 lg:p-8 max-w-md w-full animate-slide-up">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-display text-xl font-medium text-gray-900">Create New User</h3>
                <button onClick={() => setShowCreateModal(false)} className="p-2 text-gray-400 hover:text-gray-600">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">First Name *</label>
                    <input
                      type="text"
                      value={formData.firstName}
                      onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                      className="input"
                      placeholder="John"
                      required
                    />
                  </div>
                  <div>
                    <label className="label">Last Name *</label>
                    <input
                      type="text"
                      value={formData.lastName}
                      onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                      className="input"
                      placeholder="Doe"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="label">Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="input"
                    placeholder="john@example.com"
                    required
                  />
                </div>
                <div>
                  <label className="label">Password *</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="input"
                    placeholder="••••••••"
                    required
                    minLength={8}
                  />
                </div>
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="input"
                    placeholder="+351 XXX XXX XXX"
                  />
                </div>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.isAdmin}
                    onChange={(e) => setFormData({...formData, isAdmin: e.target.checked})}
                    className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Make Admin</span>
                </label>
                <div className="flex space-x-3 pt-4 border-t border-gray-100">
                  <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary flex-1">Cancel</button>
                  <button type="submit" disabled={creating} className="btn-primary flex-1">
                    {creating ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : 'Create User'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}