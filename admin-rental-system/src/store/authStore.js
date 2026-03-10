import { defineStore } from 'pinia'
// this is used to fetch the local nest backend
const API_URL = 'http://localhost:3000/admin'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    admin: null,
    token: localStorage.getItem('admin_token') || null
  }),
  actions: {
    async login(email, password) {
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.message || 'Login failed')
      localStorage.setItem('admin_token', data.accessToken)
      this.admin = data.admin
      this.token = data.accessToken
    },

    async register(credentials) {
      const res = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.message || 'Registration failed')
      return data
    },

    logout() {
      this.admin = null
      this.token = null
      localStorage.removeItem('admin_token')
    }
  }
})
