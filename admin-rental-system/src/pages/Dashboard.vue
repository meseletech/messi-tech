<template>
  <div class="dashboard">
    <!-- AI ALERT -->
    <div v-if="aiAlertMessage" class="ai-alert">
      🚨 {{ aiAlertMessage }}
    </div>

    <!-- TOTAL CARDS -->
    <div class="stats-grid">
      <div class="stat-card light-card" @click="toggleSection('merchants')">
        <p>Total Merchants</p>
        <h3>{{ totalMerchants }}</h3>
      </div>
      <div class="stat-card light-card" @click="toggleSection('customers')">
        <p>Total Customers</p>
        <h3>{{ totalCustomers }}</h3>
      </div>
      <div class="stat-card light-card" @click="toggleSection('bookings')">
        <p>Total Bookings</p>
        <h3>{{ totalBookings }}</h3>
      </div>
      <div class="stat-card yellow-card" @click="fetchAIMetrics">
        <p>AI Risk Avg</p>
        <h3>{{ aiRiskAvg }}%</h3>
      </div>
    </div>

    <!-- MERCHANTS SECTION -->
    <div v-if="activeSection === 'merchants'" class="sub-grid">
      <div class="stat-card green-card" @click="showList('merchants','active')">
        <p>Active Merchants</p>
        <h3>{{ activeMerchants }}</h3>
      </div>
      <div class="stat-card red-card" @click="showList('merchants','suspended')">
        <p>Suspended Merchants</p>
        <h3>{{ suspendedMerchants }}</h3>
      </div>
    </div>

    <!-- CUSTOMERS SECTION -->
    <div v-if="activeSection === 'customers'" class="sub-grid">
      <div class="stat-card green-card" @click="showList('customers','active')">
        <p>Active Customers</p>
        <h3>{{ activeCustomers }}</h3>
      </div>
      <div class="stat-card red-card" @click="showList('customers','suspended')">
        <p>Suspended Customers</p>
        <h3>{{ suspendedCustomers }}</h3>
      </div>
    </div>

    <!-- BOOKINGS SECTION -->
    <div v-if="activeSection === 'bookings'">
      <div class="sub-grid">
        <div v-for="(count, status) in bookingStatuses" :key="status" class="stat-card yellow-card" @click="filterBookings(status)">
          <p>{{ status.toUpperCase() }}</p>
          <h3>{{ count }}</h3>
        </div>
        <div class="stat-card" @click="resetFilter">
          <p>ALL</p>
          <h3>{{ totalBookings }}</h3>
        </div>
      </div>

      <!-- Chart -->
      <div class="chart-section">
        <canvas id="bookingChart"></canvas>
      </div>

      <!-- Booking Cards -->
      <div class="booking-grid">
        <div v-for="booking in filteredBookings" :key="booking._id" class="booking-card" @click="openModal(booking)">
          <img :src="booking.image || defaultImage" class="booking-image"/>
          <div class="booking-info">
            <h4>{{ booking.customerName || 'Customer' }}</h4>
            <p>Merchant: {{ booking.merchantName || 'Merchant' }}</p>
            <p>Date: {{ formatDate(booking.createdAt) }}</p>
            <span :class="['status-badge', booking.status?.toLowerCase()]">{{ booking.status }}</span>
            <div class="risk-score" :class="riskClass(booking.aiRiskScore)">
              AI Risk: {{ booking.aiRiskScore || 0 }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- LIST TABLE -->
    <div v-if="selectedList.length" class="list-section">
      <h3>{{ listTitle }}</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in selectedList" :key="item._id">
            <td>{{ item.name || item.fullName }}</td>
            <td>{{ item.email }}</td>
            <td>
              <span :class="item.isActive ? 'active-badge' : 'suspended-badge'">
                {{ item.isActive ? 'Active' : 'Suspended' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- BOOKING MODAL -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="selectedBooking = null">
      <div class="modal">
        <h3>Booking Details</h3>
        <img :src="selectedBooking.image || defaultImage" class="modal-image"/>
        <p><strong>Customer:</strong> {{ selectedBooking.customerName }}</p>
        <p><strong>Merchant:</strong> {{ selectedBooking.merchantName }}</p>
        <p><strong>Status:</strong> {{ selectedBooking.status }}</p>
        <p><strong>AI Risk:</strong> {{ selectedBooking.aiRiskScore || 0 }}%</p>
        <p><strong>Date:</strong> {{ formatDate(selectedBooking.createdAt) }}</p>
        <button class="close-btn" @click="selectedBooking = null"> Close </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import Chart from "chart.js/auto";
import { getAIAnalytics, getFraudDetection, getMerchantRisk } from "@/services/aiService";
import axios from "axios";

export default {
  setup() {
    const activeSection = ref(null);
    const selectedList = ref([]);
    const listTitle = ref("");
    const selectedBooking = ref(null);
    const merchantsData = ref([]);
    const customersData = ref([]);
    const bookingsData = ref([]);
    const filteredBookings = ref([]);
    const totalMerchants = ref(0);
    const activeMerchants = ref(0);
    const suspendedMerchants = ref(0);
    const totalCustomers = ref(0);
    const activeCustomers = ref(0);
    const suspendedCustomers = ref(0);
    const totalBookings = ref(0);
    const bookingStatuses = ref({});
    const aiRiskAvg = ref(0);
    const aiAlertMessage = ref(null);
    const defaultImage = "https://via.placeholder.com/300x200.png?text=No+Image";
    const chartInstance = ref(null);

    const toggleSection = (section) => {
      activeSection.value = activeSection.value === section ? null : section;
      selectedList.value = [];
      if(section === "bookings") nextTick(() => createChart());
    };

    const showList = (type, status) => {
      let data = type === "merchants" ? merchantsData.value : customersData.value;
      selectedList.value = data.filter(item => status === "active" ? item.isActive : !item.isActive);
      listTitle.value = `${status.charAt(0).toUpperCase() + status.slice(1)} ${type}`;
    };

    const formatDate = (date) => new Date(date).toLocaleDateString();
    const filterBookings = (status) => { filteredBookings.value = bookingsData.value.filter(b => b.status?.toLowerCase() === status); };
    const resetFilter = () => { filteredBookings.value = bookingsData.value; };
    const openModal = (booking) => { selectedBooking.value = booking; };
    const riskClass = (score) => score >= 70 ? "high-risk" : score >= 40 ? "medium-risk" : "low-risk";

    const createChart = () => {
      nextTick(() => {
        const ctx = document.getElementById("bookingChart");
        if (!ctx) return;
        if (chartInstance.value) chartInstance.value.destroy();
        chartInstance.value = new Chart(ctx, {
          type: "bar",
          data: {
            labels: Object.keys(bookingStatuses.value),
            datasets: [{ label: "Bookings by Status", data: Object.values(bookingStatuses.value) }]
          },
        });
      });
    };

    const fetchAIMetrics = async () => {
      try {
        const analytics = await getAIAnalytics();
        const fraud = await getFraudDetection();
        const risk = await getMerchantRisk();

        // Merge AI risk
        if (analytics?.bookings?.length) {
          const map = {};
          bookingsData.value.forEach(b => map[b._id] = b);
          analytics.bookings.forEach(a => { if(map[a._id]) map[a._id].aiRiskScore = a.aiRiskScore || 0; });
        }

        // Average risk
        const risks = analytics?.bookings?.map(b => b.aiRiskScore || 0) || [];
        aiRiskAvg.value = risks.length ? Math.round(risks.reduce((a,b)=>a+b,0)/risks.length) : 0;

        // Fraud alerts
        const alerts = fraud?.alerts || [];
        aiAlertMessage.value = alerts.length ? `⚠️ Fraud detected: ${alerts.length} alerts!` : null;

        createChart();
      } catch(err) {
        console.error(err);
        aiAlertMessage.value = "Failed to fetch AI metrics.";
      }
    };

    const fetchDashboardData = async () => {
      const token = localStorage.getItem("adminToken") || localStorage.getItem("managerToken");
      if (!token) return alert("No token found! Please login.");

      // MERCHANTS
      const merchantsRes = await axios.get("https://lmgtech-4.onrender.com/merchant/all", { headers: { Authorization: `Bearer ${token}` }});
      merchantsData.value = merchantsRes.data || [];
      totalMerchants.value = merchantsData.value.length;
      activeMerchants.value = merchantsData.value.filter(m=>m.isActive).length;
      suspendedMerchants.value = merchantsData.value.filter(m=>!m.isActive).length;

      // CUSTOMERS
      const customersRes = await axios.get("https://lmgtech-4.onrender.com/customer/all", { headers: { Authorization: `Bearer ${token}` }});
      customersData.value = customersRes.data?.customers || [];
      totalCustomers.value = customersData.value.length;
      activeCustomers.value = customersData.value.filter(c=>c.isActive).length;
      suspendedCustomers.value = customersData.value.filter(c=>!c.isActive).length;

      // BOOKINGS
      const bookingsRes = await axios.get("https://lmgtech-4.onrender.com/customer/bookings/all", { headers: { Authorization: `Bearer ${token}` }});
      bookingsData.value = bookingsRes.data?.bookings || [];
      filteredBookings.value = bookingsData.value;
      totalBookings.value = bookingsData.value.length;

      // Booking statuses
      const counts = {};
      bookingsData.value.forEach(b => { const s = b.status?.toLowerCase() || "unknown"; counts[s] = (counts[s]||0)+1; });
      bookingStatuses.value = counts;

      await fetchAIMetrics();
      createChart();
    };

    onMounted(() => fetchDashboardData());
    onUnmounted(() => { if(chartInstance.value) chartInstance.value.destroy(); });

    return {
      activeSection, toggleSection, showList, totalMerchants, activeMerchants, suspendedMerchants,
      totalCustomers, activeCustomers, suspendedCustomers, totalBookings, bookingStatuses,
      filteredBookings, filterBookings, resetFilter, selectedList, listTitle, formatDate,
      defaultImage, openModal, selectedBooking, aiAlertMessage, aiRiskAvg, fetchAIMetrics, riskClass
    };
  }
};
</script>
<style scoped>
/* ===== BASE LAYOUT ===== */
.dashboard { padding: 24px; background: #f8fafc; min-height: 100vh; }
.title { font-size: 28px; font-weight: 700; margin-bottom: 24px; }
/* ===== GRID SYSTEM ===== */
.stats-grid, .sub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-bottom: 24px; }
/* ===== CARDS ===== */
.stat-card { background: #ffffff; border-radius: 14px; padding: 20px; box-shadow: 0 6px 18px rgba(0,0,0,0.05); cursor: pointer; transition: 0.25s ease; text-align: center; }
.stat-card:hover { transform: translateY(-5px); }
.green-card { border-left: 6px solid #22c55e; }
.red-card { border-left: 6px solid #ef4444; }
.yellow-card { border-left: 6px solid #f59e0b; }
.light-card { border-left: 6px solid #3b82f6; }
/* ===== BOOKINGS GRID ===== */
.booking-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
.booking-card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.06); transition: 0.25s ease; cursor: pointer; }
.booking-card:hover { transform: translateY(-6px); }
.booking-image { width: 100%; height: 200px; object-fit: cover; }
.booking-info { padding: 16px; }
.booking-info h4 { font-size: 16px; margin-bottom: 6px; }
/* ===== STATUS BADGES ===== */
.status-badge { display: inline-block; margin-top: 8px; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.accepted { background: #dcfce7; color: #166534; }
.pending { background: #fef9c3; color: #854d0e; }
.decline { background: #fee2e2; color: #991b1b; }
.cancelled { background: #e5e7eb; color: #374151; }
.confirmed { background: #dbeafe; color: #1e40af; }
/* ===== TABLE ===== */
.list-section { margin-top: 30px; overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; background: white; min-width: 500px; }
.data-table th, .data-table td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.active-badge { background: #dcfce7; color: #166534; padding: 5px 12px; border-radius: 12px; }
.suspended-badge { background: #fee2e2; color: #991b1b; padding: 5px 12px; border-radius: 12px; }
/* ===== CHART ===== */
.chart-section { background: white; padding: 20px; border-radius: 14px; margin-bottom: 20px; overflow-x: auto; }
/* ===== MODAL ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: flex; justify-content: center; align-items: center; padding: 20px; z-index: 999; }
.modal { background: white; border-radius: 16px; width: 100%; max-width: 450px; padding: 25px; animation: fadeIn 0.3s ease; }
.modal-image { width: 100%; height: 200px; object-fit: cover; border-radius: 12px; margin-bottom: 15px; }
.close-btn { margin-top: 15px; padding: 10px 18px; border-radius: 10px; background: #3b82f6; color: white; border: none; cursor: pointer; }
.close-btn:hover { background: #2563eb; }
/* ===== MOBILE OPTIMIZATION ===== */
@media (max-width: 768px) {
  .dashboard { padding: 15px; }
  .title { font-size: 22px; }
  .stats-grid, .sub-grid { grid-template-columns: 1fr; }
  .booking-grid { grid-template-columns: 1fr; }
  .booking-image { height: 180px; }
  .modal { max-width: 95%; }
  .data-table { min-width: 400px; }
}
@media (max-width: 480px) {
  .title { font-size: 20px; }
  .stat-card { padding: 15px; }
  .booking-image { height: 160px; }
  .modal-image { height: 160px; }
}
/* ===== ANIMATION ===== */
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>