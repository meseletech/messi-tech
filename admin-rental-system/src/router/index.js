import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/pages/auth/Login.vue'
import Register from '@/pages/auth/Register.vue'

const isAuthenticated = () => !!localStorage.getItem('adminToken')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },

    // Public routes
    { path: '/login', component: Login },
    { path: '/register', component: Register },

    // Protected routes
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        { path: 'dashboard', component: () => import('@/pages/Dashboard.vue') },
        { path: 'merchant-list', component: () => import('@/pages/MerchantList.vue') },
        { path: 'customer-list', component: () => import('@/pages/CustomerList.vue') },
        { path: 'booking-list', component: () => import('@/pages/BookingList.vue') }
      ]
    },

    { path: '/:pathMatch(.*)*', redirect: '/login' }
  ]
})

/* GLOBAL AUTH GUARD */

router.beforeEach((to, from, next) => {

  const token = localStorage.getItem('adminToken')

  // if route requires auth and token is missing
  if (to.path !== '/login' && to.path !== '/register' && !token) {
    next('/login')
  } else {
    next()
  }

})

export default router