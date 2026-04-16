<template>
  <div class="dashboard">
    <div class="header">
      <h1 class="title">{{ t('dashboard.title') }}</h1>
      <p class="subtitle">{{ t('dashboard.subtitle') }}</p>
    </div>

    <!-- AI ALERT -->
    <div v-if="aiAlertMessage" class="ai-alert">
      <ExclamationTriangleIcon class="icon-sm" />
      {{ aiAlertMessage }}
    </div>

   
    <div class="ai-summary-grid">
      <div class="stat-card yellow-card">
        <ExclamationTriangleIcon class="card-icon" />
        <p>{{ t('dashboard.fraudAlerts') }}</p>
        <h3>{{ aiAlerts.length }}</h3>
      </div>
      <div class="stat-card red-card">
        <ShieldCheckIcon class="card-icon" />
        <p>{{ t('dashboard.highRiskMerchants') }}</p>
        <h3>{{ highRiskMerchantCount }}</h3>
      </div>
      <div class="stat-card green-card">
        <UserGroupIcon class="card-icon" />
        <p>{{ t('dashboard.merchantRiskItems') }}</p>
        <h3>{{ merchantRiskCount }}</h3>
      </div>
    </div>

    <!-- TOTAL CARDS -->
    <div class="stats-grid">
      <div class="stat-card light-card" @click="toggleSection('merchants')">
        <UserGroupIcon class="card-icon" />
        <p>{{ t('dashboard.totalMerchants') }}</p>
        <h3>{{ totalMerchants }}</h3>
      </div>
      <div class="stat-card light-card" @click="toggleSection('customers')">
        <UserIcon class="card-icon" />
        <p>{{ t('dashboard.totalCustomers') }}</p>
        <h3>{{ totalCustomers }}</h3>
      </div>
      <button type="button" class="stat-card light-card card-button" @click="showBookings">
        <DocumentTextIcon class="card-icon" />
        <p>{{ t('dashboard.totalBookings') }}</p>
        <h3>{{ totalBookings }}</h3>
      </button>
      <div class="stat-card yellow-card" @click="fetchAIMetrics">
        <ExclamationTriangleIcon class="card-icon" />
        <p>{{ t('dashboard.aiRiskAvg') }}</p>
        <h3>{{ aiRiskAvg }}%</h3>
      </div>
    </div>

    <!-- AI DETAILS -->
    <div class="ai-details" v-if="aiAlerts.length || merchantRisks.length">
      <div class="ai-widget">
        <h3>{{ t('dashboard.fraudAlertsTitle') }}</h3>
        <div v-if="aiAlerts.length" class="ai-list">
          <div v-for="alert in aiAlerts.slice(0, 6)" :key="alert.userId + alert.riskReason" class="ai-list-item">
            <span class="badge">{{ alert.role.toUpperCase() }}</span>
            <div>
              <p>{{ alert.message || (alert.role === 'merchant' ? 'Merchant' : 'User') + ' flagged' }}</p>
              <small>{{ alert.riskReason }} · score {{ alert.riskScore || 0 }}</small>
            </div>
          </div>
        </div>
        <p v-else class="ai-empty">{{ t('dashboard.noFraudAlerts') }}</p>
      </div>
      <div class="ai-widget">
        <h3>{{ t('dashboard.merchantRiskTitle') }}</h3>
        <div v-if="merchantRisks.length" class="ai-list">
          <div v-for="merchant in merchantRisks.slice(0, 6)" :key="merchant.merchantId" class="ai-list-item">
            <span class="badge">{{ merchant.riskLevel }}</span>
            <div>
              <p>{{ t('dashboard.merchantLabel') }} {{ merchant.name || merchant.merchantId }}</p>
              <small>{{ t('dashboard.riskScore') }} {{ Math.round((merchant.riskProbability || 0) * 100) / 100 }}</small>
            </div>
          </div>
        </div>
        <p v-else class="ai-empty">{{ t('dashboard.noMerchantRisk') }}</p>
      </div>
    </div>

    <!-- MERCHANTS SECTION -->
    <div v-if="activeSection === 'merchants'" class="sub-grid">
      <div class="stat-card green-card" @click="showList('merchants','active')">
        <UserGroupIcon class="card-icon" />
        <p>{{ t('dashboard.activeMerchants') }}</p>
        <h3>{{ activeMerchants }}</h3>
      </div>
      <div class="stat-card red-card" @click="showList('merchants','suspended')">
        <ExclamationTriangleIcon class="card-icon" />
        <p>{{ t('dashboard.suspendedMerchants') }}</p>
        <h3>{{ suspendedMerchants }}</h3>
      </div>
    </div>

    <!-- CUSTOMERS SECTION -->
    <div v-if="activeSection === 'customers'" class="sub-grid">
      <div class="stat-card green-card" @click="showList('customers','active')">
        <UserIcon class="card-icon" />
        <p>{{ t('dashboard.activeCustomers') }}</p>
        <h3>{{ activeCustomers }}</h3>
      </div>
      <div class="stat-card red-card" @click="showList('customers','suspended')">
        <ExclamationTriangleIcon class="card-icon" />
        <p>{{ t('dashboard.suspendedCustomers') }}</p>
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
      <div class="chart-section" ref="bookingChartSection">
        <h4 class="chart-title">Booking Risk Levels</h4>
        <canvas ref="bookingChartCanvas"></canvas>
      </div>

      <!-- Booking Cards -->
      <div class="booking-grid">
        <div v-for="booking in filteredBookings" :key="booking._id" class="booking-card" @click="openModal(booking)">
          <img :src="getBookingImage(booking)" @error="$event.target.src = defaultImage" class="booking-image"/>
          <div class="booking-info">
            <h4>{{ booking.customerName || 'Customer' }}</h4>
            <p>Merchant: {{ booking.merchantName || 'Merchant' }}</p>
            <p>Date: {{ formatDate(booking) }}</p>
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
            <th>{{ t('dashboard.name') }}</th>
            <th>{{ t('dashboard.email') }}</th>
            <th>{{ t('dashboard.status') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in selectedList" :key="item._id">
            <td>{{ item.name || item.fullName }}</td>
            <td>{{ item.email }}</td>
            <td>
              <span :class="item.isActive ? 'active-badge' : 'suspended-badge'">
                {{ item.isActive ? t('dashboard.active') : t('dashboard.suspended') }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- BOOKING MODAL -->
    <div v-if="selectedBooking" class="modal-overlay" @click.self="selectedBooking = null">
      <div class="modal">
        <h3>{{ t('dashboard.bookingDetails') }}</h3>
        <img :src="getBookingImage(selectedBooking)" @error="$event.target.src = defaultImage" class="modal-image"/>
        <p><strong>{{ t('dashboard.customer') }}:</strong> {{ selectedBooking.customerName }}</p>
        <p><strong>{{ t('dashboard.merchant') }}:</strong> {{ selectedBooking.merchantName }}</p>
        <p><strong>{{ t('dashboard.bookingStatus') }}:</strong> {{ selectedBooking.status }}</p>
        <p><strong>{{ t('dashboard.aiRisk') }}:</strong> {{ selectedBooking.aiRiskScore || 0 }}%</p>
        <p><strong>{{ t('dashboard.date') }}:</strong> {{ formatDate(selectedBooking) }}</p>
        <button class="close-btn" @click="selectedBooking = null"> <XMarkIcon class="icon-sm" /> {{ t('dashboard.close') }} </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import Chart from "chart.js/auto";
import { getAIAnalytics, getFraudDetection, getMerchantRisk, retrainFraudModel, retrainMerchantModel } from "@/services/aiService";
import axios from "axios";
import { UserGroupIcon, UserIcon, DocumentTextIcon, ExclamationTriangleIcon, ShieldCheckIcon, XMarkIcon } from "@heroicons/vue/24/outline";
import { useI18n } from 'vue-i18n';

export default {
  setup() {
    const { t } = useI18n();
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
    const aiAlerts = ref([]);
    const merchantRisks = ref([]);
    const merchantRiskCount = ref(0);
    const highRiskMerchantCount = ref(0);
    const aiAlertMessage = ref(null);
    const retrainingFraud = ref(false);
    const retrainingMerchant = ref(false);
    const defaultImage = "https://via.placeholder.com/300x200.png?text=No+Image";
    const API_ORIGIN = "https://lmgtech-e1q0.onrender.com";
    const chartInstance = ref(null);
    const bookingChartSection = ref(null);
    const bookingChartCanvas = ref(null);

    const toggleSection = (section) => {
      if (section === "bookings") {
        showBookings();
        return;
      }

      activeSection.value = activeSection.value === section ? null : section;
      selectedList.value = [];
    };

    const showBookings = async () => {
      activeSection.value = "bookings";
      selectedList.value = [];
      filteredBookings.value = bookingsData.value;
      await nextTick();
      createChart();
      bookingChartSection.value?.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    const showList = (type, status) => {
      let data = type === "merchants" ? merchantsData.value : customersData.value;
      selectedList.value = data.filter(item => status === "active" ? item.isActive : !item.isActive);
      listTitle.value = `${status.charAt(0).toUpperCase() + status.slice(1)} ${type}`;
    };

    const formatDate = (value) => {
      const fallback = "N/A";

      const extractDateCandidate = (input) => {
        if (!input) return null;

        if (typeof input === "string" || typeof input === "number" || input instanceof Date) {
          return input;
        }

        if (typeof input === "object") {
          return (
            input.createdAt ||
            input.startDate ||
            input.bookingDate ||
            input.date ||
            input.updatedAt ||
            input?.created_at ||
            input?.$date ||
            null
          );
        }

        return null;
      };

      const candidate = extractDateCandidate(value);
      if (!candidate) return fallback;

      const normalized = typeof candidate === "object" && candidate?.$date ? candidate.$date : candidate;
      const parsed = new Date(normalized);

      if (Number.isNaN(parsed.getTime())) return fallback;

      return parsed.toLocaleDateString();
    };

    const getBookingStatus = (booking) => {
      return (booking.status || booking.bookingStatus || booking.state || "unknown").toString();
    };

    const normalizeImageUrl = (value) => {
      if (!value || typeof value !== "string") return null;
      if (/^https?:\/\//i.test(value)) return value;
      if (value.startsWith("//")) return `https:${value}`;
      if (value.startsWith("/")) return `${API_ORIGIN}${value}`;
      return value;
    };

    const getBookingImage = (booking) => {
      if (!booking) return defaultImage;

      const candidates = [
        booking.image,
        booking.photo,
        booking.coverImage,
        booking.picture,
        booking.vehicleImage,
        booking.carImage,
        booking.propertyImage,
        booking.imageUrls?.[0],
        booking.images?.[0],
        booking.property?.image,
        booking.property?.coverImage,
        booking.property?.imageUrls?.[0],
        booking.property?.images?.[0],
        booking.asset?.image,
        booking.asset?.imageUrls?.[0],
        booking.asset?.images?.[0],
        booking.customer?.avatar,
        booking.merchant?.logo,
      ];

      for (const candidate of candidates) {
        const normalized = normalizeImageUrl(candidate);
        if (normalized) return normalized;
      }

      return defaultImage;
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
      createChart();
    };

    const resetFilter = () => {
      filteredBookings.value = bookingsData.value;
      createChart();
    };
    const openModal = (booking) => { selectedBooking.value = booking; };
    const riskClass = (score) => score >= 70 ? "high-risk" : score >= 40 ? "medium-risk" : "low-risk";

    const destroyChart = () => {
      if (!chartInstance.value) return;
      try {
        if (typeof chartInstance.value.stop === "function") {
          chartInstance.value.stop();
        }
        chartInstance.value.destroy();
      } catch (e) {
        console.warn("Chart cleanup warning:", e);
      } finally {
        chartInstance.value = null;
      }
    };

    const createChart = () => {
      if (activeSection.value !== "bookings") return;

      const canvas = bookingChartCanvas.value;
      if (!canvas || !canvas.isConnected) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      destroyChart();

        const chartLabels = filteredBookings.value.map((booking, index) => {
          return booking.customerName || booking.merchantName || `Booking ${index + 1}`;
        });
        const chartData = filteredBookings.value.map((booking) => {
          const parsed = Number.parseFloat(booking.aiRiskScore);
          return Number.isFinite(parsed) ? parsed : 0;
        });

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
            animation: false,
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
    };

    const fetchAIMetrics = async () => {
      try {
        const analytics = await getAIAnalytics();
        const fraud = await getFraudDetection();
        const risk = await getMerchantRisk();

        merchantRisks.value = Array.isArray(risk)
          ? risk
          : risk?.merchantRisk || [];
        merchantRisks.value.forEach(mr => {
          const merchant = merchantsData.value.find(m => m._id === mr.merchantId);
          if (merchant) mr.name = merchant.name || merchant.fullName;
        });
        merchantRiskCount.value = merchantRisks.value.length;
        highRiskMerchantCount.value = merchantRisks.value.filter((m) => m.riskLevel === "HIGH").length;

        aiAlerts.value = fraud?.fraudCases || [];

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
        if (totalFrauds > 0) {
          aiAlertMessage.value = `⚠️ Fraud detected: ${totalFrauds} suspicious cases!`;
        } else if (highRiskMerchantCount.value > 0) {
          aiAlertMessage.value = `⚠️ ${highRiskMerchantCount.value} high-risk merchants detected.`;
        } else {
          aiAlertMessage.value = null;
        }

        const counts = {};
        bookingsData.value.forEach((b) => {
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
      const merchantsRes = await axios.get("https://lmgtech-e1q0.onrender.com/merchant/all", { headers: { Authorization: `Bearer ${token}` }});
      merchantsData.value = merchantsRes.data || [];
      totalMerchants.value = merchantsData.value.length;
      activeMerchants.value = merchantsData.value.filter(m=>m.isActive).length;
      suspendedMerchants.value = merchantsData.value.filter(m=>!m.isActive).length;

      // CUSTOMERS
      const customersRes = await axios.get("https://lmgtech-e1q0.onrender.com/customer/all", { headers: { Authorization: `Bearer ${token}` }});
      customersData.value = customersRes.data?.customers || [];
      totalCustomers.value = customersData.value.length;
      activeCustomers.value = customersData.value.filter(c=>c.isActive).length;
      suspendedCustomers.value = customersData.value.filter(c=>!c.isActive).length;

      // BOOKINGS
      const bookingsRes = await axios.get("https://lmgtech-e1q0.onrender.com/customer/bookings/all", { headers: { Authorization: `Bearer ${token}` }});
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

    watch(filteredBookings, () => {
      if (activeSection.value === "bookings") createChart();
    }, { deep: true });

    watch(activeSection, (section) => {
      if (section === "bookings") {
        nextTick(() => createChart());
      } else {
        destroyChart();
      }
    });

    onUnmounted(() => { destroyChart(); });

    return {
      activeSection, toggleSection, showBookings, showList, totalMerchants, activeMerchants, suspendedMerchants,
      totalCustomers, activeCustomers, suspendedCustomers, totalBookings, bookingStatuses,
      filteredBookings, filterBookings, resetFilter, selectedList, listTitle, formatDate,
      defaultImage, openModal, selectedBooking, aiAlertMessage, aiRiskAvg, aiAlerts, merchantRisks, getBookingImage,
      merchantRiskCount, highRiskMerchantCount, fetchAIMetrics, riskClass,
      retrainingFraud, retrainingMerchant, handleRetrainFraud, handleRetrainMerchant,
      UserGroupIcon, UserIcon, DocumentTextIcon, ExclamationTriangleIcon, ShieldCheckIcon, XMarkIcon,
      t, bookingChartSection, bookingChartCanvas
    };
  }
};
</script>
<style scoped>
/* ===== BASE LAYOUT ===== */
.dashboard { padding: 24px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); min-height: 100vh; }
.dark .dashboard { background: linear-gradient(135deg, #1f2937 0%, #111827 100%); }
.header { margin-bottom: 32px; text-align: center; }
.title { font-size: 32px; font-weight: 800; margin-bottom: 8px; color: #1f2937; }
.dark .title { color: #f9fafb; }
.subtitle { font-size: 16px; color: #6b7280; margin: 0; }
.dark .subtitle { color: #9ca3af; }
/* ===== AI ALERT ===== */
.ai-alert { background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); color: #991b1b; padding: 16px 24px; border-radius: 12px; margin-bottom: 24px; font-weight: 600; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1); }
.dark .ai-alert { background: linear-gradient(135deg, #451a1a 0%, #7f1d1d 100%); color: #fca5a5; }
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
.stat-card { background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%); border-radius: 16px; padding: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.3s ease; text-align: center; position: relative; border: 1px solid #e5e7eb; }
.dark .stat-card { background: linear-gradient(135deg, #374151 0%, #1f2937 100%); border: 1px solid #4b5563; }
.card-button { width: 100%; appearance: none; -webkit-appearance: none; font: inherit; color: inherit; background: inherit; }
.stat-card:hover { transform: translateY(-8px); box-shadow: 0 16px 40px rgba(0,0,0,0.15); }
.card-icon { width: 32px; height: 32px; margin: 0 auto 8px; color: #6b7280; }
.icon-sm { width: 16px; height: 16px; margin-right: 8px; }
.green-card { border-top: 6px solid #22c55e; }
.green-card .card-icon { color: #22c55e; }
.red-card { border-top: 6px solid #ef4444; }
.red-card .card-icon { color: #ef4444; }
.yellow-card { border-top: 6px solid #f59e0b; }
.yellow-card .card-icon { color: #f59e0b; }
.light-card { border-top: 6px solid #3b82f6; }
.light-card .card-icon { color: #3b82f6; }
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
.dark .data-table { background: #1f2937; color: #f9fafb; }
.data-table th, .data-table td { padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }
.dark .data-table th, .dark .data-table td { border-bottom: 1px solid #4b5563; }
.active-badge { background: #dcfce7; color: #166534; padding: 5px 12px; border-radius: 12px; }
.dark .active-badge { background: #14532d; color: #bbf7d0; }
.suspended-badge { background: #fee2e2; color: #991b1b; padding: 5px 12px; border-radius: 12px; }
.dark .suspended-badge { background: #7f1d1d; color: #fca5a5; }
/* ===== CHART ===== */
.chart-section { background: white; padding: 20px; border-radius: 14px; margin-bottom: 20px; overflow-x: auto; }
.chart-title { margin: 0 0 12px; font-size: 16px; font-weight: 700; }
.ai-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 18px; margin-bottom: 24px; }
.ai-details { display: grid; grid-template-columns: repeat(2, minmax(260px, 1fr)); gap: 18px; margin-bottom: 24px; }
.ai-widget { background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%); border-radius: 16px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; }
.dark .ai-widget { background: linear-gradient(135deg, #374151 0%, #1f2937 100%); border: 1px solid #4b5563; }
.ai-widget h3 { margin: 0 0 12px; font-size: 16px; }
.ai-list { display: grid; gap: 12px; }
.ai-list-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; border: 1px solid #e5e7eb; border-radius: 12px; }
.ai-list-item .badge { padding: 6px 10px; border-radius: 999px; background: #e0f2fe; color: #0369a1; font-size: 11px; font-weight: 700; }
.ai-empty { margin: 0; color: #6b7280; }
/* ===== MODAL ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.55); display: flex; justify-content: center; align-items: center; padding: 20px; z-index: 999; }
.dark .modal-overlay { background: rgba(0,0,0,0.75); }
.modal { background: white; border-radius: 16px; width: 100%; max-width: 450px; padding: 25px; animation: fadeIn 0.3s ease; }
.dark .modal { background: #1f2937; color: #f9fafb; }
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
.stats-grid, .sub-grid, .ai-summary-grid, .ai-details { animation: fadeInUp 0.6s ease-out; }
</style>
