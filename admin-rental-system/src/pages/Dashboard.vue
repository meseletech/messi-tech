<template>
  <div class="dashboard">
    <h2 class="title">Admin Dashboard</h2>

    <!-- AI ALERT BANNER -->
    <div v-if="aiAlertMessage" class="ai-alert">
      🚨 {{ aiAlertMessage }}
    </div>

    <!-- MAIN TOTAL CARDS -->
    <div class="stats-grid">

      <div class="stat-card light-card"
           @click="toggleSection('merchants')">
        <p class="stat-label">Total Merchants</p>
        <p class="stat-value">{{ totalMerchants }}</p>
      </div>

      <div class="stat-card light-card"
           @click="toggleSection('customers')">
        <p class="stat-label">Total Customers</p>
        <p class="stat-value">{{ totalCustomers }}</p>
      </div>

      <div class="stat-card light-card"
           @click="toggleSection('bookings')">
        <p class="stat-label">Total Bookings</p>
        <p class="stat-value">{{ totalBookings }}</p>
      </div>

    </div>

    <!-- MERCHANT DETAILS -->
    <div v-if="activeSection === 'merchants'" class="sub-grid">
      <div class="stat-card green-card">
        <p class="stat-label">Active Merchants</p>
        <p class="stat-value">{{ activeMerchants }}</p>
      </div>

      <div class="stat-card red-card">
        <p class="stat-label">Suspended Merchants</p>
        <p class="stat-value">{{ suspendedMerchants }}</p>
      </div>
    </div>

    <!-- CUSTOMER DETAILS -->
    <div v-if="activeSection === 'customers'" class="sub-grid">
      <div class="stat-card green-card">
        <p class="stat-label">Active Customers</p>
        <p class="stat-value">{{ activeCustomers }}</p>
      </div>

      <div class="stat-card red-card">
        <p class="stat-label">Suspended Customers</p>
        <p class="stat-value">{{ suspendedCustomers }}</p>
      </div>
    </div>

    <!-- BOOKING DETAILS -->
    <div v-if="activeSection === 'bookings'" class="sub-grid">
      <div
        v-for="(count, status) in bookingStatuses"
        :key="status"
        class="stat-card yellow-card"
      >
        <p class="stat-label">{{ status }}</p>
        <p class="stat-value">{{ count }}</p>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

export default {
  setup() {

    const toast = useToast()
    const aiAlertMessage = ref(null)

    const activeSection = ref(null)

    const totalMerchants = ref(0)
    const activeMerchants = ref(0)
    const suspendedMerchants = ref(0)

    const totalCustomers = ref(0)
    const activeCustomers = ref(0)
    const suspendedCustomers = ref(0)

    const totalBookings = ref(0)
    const bookingStatuses = ref({})

    let socket = null

    const toggleSection = (section) => {
      activeSection.value =
        activeSection.value === section ? null : section
    }

    const fetchDashboardData = async () => {
      try {
        const token =
          localStorage.getItem('adminToken') ||
          localStorage.getItem('managerToken')

        const merchantsRes = await axios.get(
          'https://lmgtech-4.onrender.com/merchant/all',
          { headers: { Authorization: `Bearer ${token}` } }
        )

        const merchants = merchantsRes.data || []
        totalMerchants.value = merchants.length
        activeMerchants.value = merchants.filter(m => m.isActive).length
        suspendedMerchants.value = merchants.filter(m => !m.isActive).length

        const customersRes = await axios.get(
          'https://lmgtech-4.onrender.com/customer/all',
          { headers: { Authorization: `Bearer ${token}` } }
        )

        const customers = customersRes.data?.customers || []
        totalCustomers.value = customers.length
        activeCustomers.value = customers.filter(c => c.isActive).length
        suspendedCustomers.value = customers.filter(c => !c.isActive).length

        const bookingsRes = await axios.get(
          'https://lmgtech-4.onrender.com/customer/bookings/all',
          { headers: { Authorization: `Bearer ${token}` } }
        )

        const bookings = bookingsRes.data?.bookings || []
        totalBookings.value = bookings.length

        const statusCounts = {
          decline: 0,
          accepted: 0,
          pending: 0,
          confirmed: 0,
          cancelled: 0
        }

        bookings.forEach(b => {
          const status = b.status?.toLowerCase()
          if (statusCounts.hasOwnProperty(status)) {
            statusCounts[status]++
          }
        })

        bookingStatuses.value = statusCounts

      } catch (error) {
        console.error("Dashboard Error:", error)
      }
    }

    const connectWebSocket = () => {
      socket = new WebSocket("ws://127.0.0.1:8001/ws/notifications")

      socket.onopen = () => {
        console.log("✅ WebSocket Connected")
      }

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === "ANALYTICS_UPDATE") {
          fetchDashboardData()
          toast.info("📊 AI Analytics Updated")
        }

        if (data.type === "FRAUD_ALERT") {
          toast.error("⚠️ Fraud Detected!")
          aiAlertMessage.value = "Fraud activity detected in system."
        }

        if (data.type === "MERCHANT_RISK_UPDATE") {
          toast.warning("🚨 High Risk Merchant Detected!")
          aiAlertMessage.value = "High-risk merchant identified."
        }
      }

      socket.onerror = (error) => {
        console.error("WebSocket Error:", error)
      }

      socket.onclose = () => {
        console.log("❌ WebSocket Disconnected")
      }
    }

    onMounted(() => {
      fetchDashboardData()
      connectWebSocket()
    })

    onUnmounted(() => {
      if (socket) socket.close()
    })

    return {
      activeSection,
      toggleSection,
      totalMerchants,
      activeMerchants,
      suspendedMerchants,
      totalCustomers,
      activeCustomers,
      suspendedCustomers,
      totalBookings,
      bookingStatuses,
      aiAlertMessage
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 25px;
  background: #f9fafb;
  min-height: 100vh;
}

.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 25px;
  color: #1f2937;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

.stat-card {
  border-radius: 14px;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-label {
  font-size: 15px;
  color: #6b7280;
}

.stat-value {
  font-size: 30px;
  font-weight: bold;
  margin-top: 8px;
  color: #111827;
}

.sub-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

.green-card {
  border-left: 6px solid #22c55e;
}

.red-card {
  border-left: 6px solid #ef4444;
}

.yellow-card {
  border-left: 6px solid #f59e0b;
}

.ai-alert {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  margin-bottom: 20px;
  border-radius: 8px;
  font-weight: 600;
}
</style>