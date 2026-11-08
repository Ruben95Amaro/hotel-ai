import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Add API key for backend
    config.headers['X-API-Key'] = 'dev-key-12345'
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const hotelApi = {
  // Hotel info
  getInfo: () => api.get('/hotel/info'),
  getServices: () => api.get('/hotel/services'),
  
  // Rooms & Availability
  getRooms: () => api.get('/hotel/rooms'),
  checkAvailability: (data) => api.post('/hotel/availability', data),
  
  // Auth
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/profile'),
  
  // Bookings
  createBooking: (data) => api.post('/bookings', data),
  getBookings: () => api.get('/bookings'),
  getBooking: (id) => api.get(`/bookings/${id}`),
  cancelBooking: (id, reason) => api.post(`/bookings/${id}/cancel`, { reason }),
  modifyBooking: (id, data) => api.put(`/bookings/${id}`, data),
  
  // Special requests
  createSpecialRequest: (data) => api.post('/special-requests', data),
  getSpecialRequests: () => api.get('/special-requests'),
  
  // Chat/AI Assistant
  chat: (message, sessionId) => api.post('/chat', { message, session_id: sessionId }),
}

export default api