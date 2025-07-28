import axios from 'axios'
import toast from 'react-hot-toast'

export const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      delete api.defaults.headers.common['Authorization']
      window.location.href = '/login'
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail)
    } else {
      toast.error('An unexpected error occurred')
    }
    return Promise.reject(error)
  }
)