<template>
  <div class="dashboard">
    <!-- AI ALERT -->
    <div v-if="aiAlertMessage" class="ai-alert">
      🚨 {{ aiAlertMessage }}
    </div>

    <!-- AI CONTROLS -->
    <div class="ai-controls">
      <button class="ai-btn" @click="handleRetrainFraud" :disabled="retrainingFraud">
        {{ retrainingFraud ? 'Retraining Fraud...' : 'Retrain Fraud Model' }}
      </button>
      <button class="ai-btn" @click="handleRetrainMerchant" :disabled="retrainingMerchant">
        {{ retrainingMerchant ? 'Retraining Merchant...' : 'Retrain Merchant Model' }}
      </button>
      <button class="ai-btn refresh-btn" @click="fetchAIMetrics">Refresh AI Data</button>
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
      <div class="stat-card light-card" @click="showBookings()">
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
      <div class="booking-section-header">
        <div class="stat-card light-card">
          <p>Total Bookings</p>
          <h3>{{ totalBookings }}</h3>
        </div>
        <div class="stat-card yellow-card">
          <p>Average AI Risk</p>
          <h3>{{ aiRiskAvg }}%</h3>
        </div>
      </div>

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
        <h4 class="chart-title">Booking Risk Levels</h4>
        <canvas id="bookingChart"></canvas>
      </div>

      <!-- Booking Cards -->
      <div class="booking-grid">
        <div v-for="booking in filteredBookings" :key="booking._id" class="booking-card" @click="openModal(booking)">
          <img :src="getBookingImage(booking)" class="booking-image"/>
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
import { getAIAnalytics, getFraudDetection, getMerchantRisk, retrainFraudModel, retrainMerchantModel } from "@/services/aiService";
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
    const retrainingFraud = ref(false);
    const retrainingMerchant = ref(false);
    const defaultImage = "https://via.placeholder.com/300x200.png?text=No+Image";
    const chartInstance = ref(null);

    const toggleSection = (section) => {
      activeSection.value = activeSection.value === section ? null : section;
      selectedList.value = [];
      if (section === "bookings") {
        filteredBookings.value = bookingsData.value;
        nextTick(() => createChart());
      }
    };

    const showBookings = () => {
      activeSection.value = "bookings";
      selectedList.value = [];
      filteredBookings.value = bookingsData.value;
      nextTick(() => createChart());
    };

    const showList = (type, status) => {
      let data = type === "merchants" ? merchantsData.value : customersData.value;
      selectedList.value = data.filter(item => status === "active" ? item.isActive : !item.isActive);
      listTitle.value = `${status.charAt(0).toUpperCase() + status.slice(1)} ${type}`;
    };

    const formatDate = (date) => new Date(date).toLocaleDateString();

    const getBookingStatus = (booking) => {
      return (booking.status || booking.bookingStatus || booking.state || "unknown").toString();
    };

    const getBookingImage = (booking) => {
      return (
        booking.image ||
        booking.photo ||
        booking.coverImage ||
        booking.picture ||
        booking.vehicleImage ||
        booking.carImage ||
        booking.customer?.avatar ||
        booking.merchant?.logo ||
        defaultImage
      );
    };

    const estimateRisk = (booking) => {
      const st = getBookingStatus(booking).toLowerCase();
      if (["cancelled", "declined", "decline"].includes(st)) return 80;
      if (st === "pending") return 55;
      if (["confirmed", "accepted"].includes(st)) return 20;
      return 40;
    };

    const filterBookings = (status) => {
      filteredBookings.value = bookingsData.value.filter(b => getBookingStatus(b).toLowerCase() === status);
    };

    const resetFilter = () => { filteredBookings.value = bookingsData.value; };
    const openModal = (booking) => { selectedBooking.value = booking; };
    const riskClass = (score) => score >= 70 ? "high-risk" : score >= 40 ? "medium-risk" : "low-risk";

    const createChart = () => {
      nextTick(() => {
        const ctx = document.getElementById("bookingChart");
        if (!ctx) return;
        if (chartInstance.value) chartInstance.value.destroy();

        const chartLabels = filteredBookings.value.map((booking, index) => {
          return booking.customerName || booking.merchantName || `Booking ${index + 1}`;
        });
        const chartData = filteredBookings.value.map((booking) => Number(booking.aiRiskScore || 0));

        chartInstance.value = new Chart(ctx, {
          type: "bar",
          data: {
            labels: chartLabels,
            datasets: [{
              label: "Booking Risk Score",
              data: chartData,
              backgroundColor: chartData.map((value) => value >= 70 ? "#f87171" : value >= 40 ? "#fbbf24" : "#34d399"),
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: { display: true, text: 'Risk (%)' }
              },
              x: {
                title: { display: true, text: 'Booking' }
              }
            },
            plugins: {
              legend: { display: false }
            }
          }
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

        // Average risk (analytics-only snapshot)
        const analyticsRisks = analytics?.bookings?.map(b => b.aiRiskScore || 0) || [];
        aiRiskAvg.value = analyticsRisks.length ? Math.round(analyticsRisks.reduce((a,b)=>a+b,0)/analyticsRisks.length) : 0;

        // Merge AI risk to bookings and fill fallback risk values
        const analyticsBookings = analytics?.bookings || [];
        const analyticsMap = new Map(analyticsBookings.map((b) => [String(b._id), Number(b.aiRiskScore || 0)]));

        bookingsData.value.forEach((booking) => {
          const idKey = String(booking._id || booking.id || "");
          const matched = analyticsMap.get(idKey);
          booking.aiRiskScore = matched != null ? matched : (booking.aiRiskScore || estimateRisk(booking));
        });

        // AI risk avg should use the final booking aiRiskScore values
        const risks = bookingsData.value.map((b) => Number(b.aiRiskScore || 0));
        aiRiskAvg.value = risks.length ? Math.round(risks.reduce((a, b) => a + b, 0) / risks.length) : 0;

        // Fraud alerts
        const totalFrauds = fraud?.totalFrauds || 0;
        aiAlertMessage.value = totalFrauds > 0 ? `⚠️ Fraud detected: ${totalFrauds} suspicious cases!` : null;

        // Update current bookings chart counts (again)
        const counts = {};
        bookingsData.value.forEach(b => {
          const status = getBookingStatus(b).toLowerCase() || "unknown";
          counts[status] = (counts[status] || 0) + 1;
        });
        bookingStatuses.value = counts;

        createChart();
      } catch(err) {
        console.error(err);
        aiAlertMessage.value = "Failed to fetch AI metrics.";
      }
    };

    const handleRetrainFraud = async () => {
      retrainingFraud.value = true;
      try {
        await retrainFraudModel();
        alert("Fraud model retrained successfully!");
        await fetchAIMetrics(); // Refresh data
      } catch(err) {
        console.error(err);
        alert("Failed to retrain fraud model.");
      } finally {
        retrainingFraud.value = false;
      }
    };

    const handleRetrainMerchant = async () => {
      retrainingMerchant.value = true;
      try {
        await retrainMerchantModel();
        alert("Merchant model retrained successfully!");
        await fetchAIMetrics(); // Refresh data
      } catch(err) {
        console.error(err);
        alert("Failed to retrain merchant model.");
      } finally {
        retrainingMerchant.value = false;
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

      // Booking statuses (normalize from all possible fields)
      const counts = {};
      bookingsData.value.forEach(b => {
        const status = getBookingStatus(b).toLowerCase() || "unknown";
        counts[status] = (counts[status] || 0) + 1;
      });
      bookingStatuses.value = counts;

      await fetchAIMetrics();
      // createChart is already called inside fetchAIMetrics when relevant

    };

    onMounted(() => fetchDashboardData());
    onUnmounted(() => { if(chartInstance.value) chartInstance.value.destroy(); });

    return {
      activeSection, toggleSection, showBookings, showList, totalMerchants, activeMerchants, suspendedMerchants,
      totalCustomers, activeCustomers, suspendedCustomers, totalBookings, bookingStatuses,
      filteredBookings, filterBookings, resetFilter, selectedList, listTitle, formatDate,
      defaultImage, openModal, selectedBooking, aiAlertMessage, aiRiskAvg, fetchAIMetrics, riskClass,
      retrainingFraud, retrainingMerchant, handleRetrainFraud, handleRetrainMerchant
    };
  }
};
</script>
<style scoped>
/* ===== BASE LAYOUT ===== */
.dashboard { padding: 24px; background: #f8fafc; min-height: 100vh; }
.title { font-size: 28px; font-weight: 700; margin-bottom: 24px; }
/* ===== AI ALERT ===== */
.ai-alert { background: #fee2e2; color: #991b1b; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; font-weight: 600; }
/* ===== AI CONTROLS ===== */
.ai-controls { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.ai-btn { background: #3b82f6; color: white; border: none; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.2s; }
.ai-btn:hover:not(:disabled) { background: #2563eb; }
.ai-btn:disabled { background: #9ca3af; cursor: not-allowed; }
.refresh-btn { background: #10b981; }
.refresh-btn:hover:not(:disabled) { background: #059669; }
.booking-section-header { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px; }
.booking-section-header .stat-card { cursor: default; }
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
/* ===== RISK SCORE ===== */
.risk-score { display: inline-block; margin-top: 8px; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.low-risk { background: #dcfce7; color: #166534; }
.medium-risk { background: #fef9c3; color: #854d0e; }
.high-risk { background: #fee2e2; color: #991b1b; }
/* ===== TABLE ===== */
.list-section { margin-top: 30px; overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; background: white; min-width: 500px; }
.data-table th, .data-table td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.active-badge { background: #dcfce7; color: #166534; padding: 5px 12px; border-radius: 12px; }
.suspended-badge { background: #fee2e2; color: #991b1b; padding: 5px 12px; border-radius: 12px; }
/* ===== CHART ===== */
.chart-section { background: white; padding: 20px; border-radius: 14px; margin-bottom: 20px; overflow-x: auto; }
.chart-title { margin: 0 0 12px; font-size: 16px; font-weight: 700; }
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