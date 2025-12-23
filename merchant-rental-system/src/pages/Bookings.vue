<template>
  <div class="booking-list-page">
    <h1 class="page-title">{{ t('bookings.title') }}</h1>

    <!-- Loading -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>{{ t('bookings.loading') }}</p>
    </div>

    <!-- Booking Grid -->
    <div v-if="!loading && bookings.length" class="bookings-grid">
      <div
        v-for="booking in bookings"
        :key="booking.bookingId"
        class="booking-card"
      >
        <div class="booking-info">
          <h2>{{ booking.propertyName }}</h2>

          <p><strong>Customer:</strong> {{ booking.customerName }}</p>
          <p><strong>Total Price:</strong> {{ booking.totalPrice }}</p>

          <!-- BOOKING STATUS -->
          <p>
            <strong>Status:</strong>
            <select
              v-model="booking.status"
              class="status-select"
              :disabled="booking.status === 'COMPLETED'"
              @change="updateBookingStatus(booking)"
            >
              <option value="PENDING">Pending</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </p>

          <!-- PAYMENT STATUS ✅ -->
          <p>
      <select
  v-model="booking.paymentStatus"
  class="status-select"
  :disabled="booking.paymentStatus === 'PAID'"
  @change="updatePaymentStatus(booking)"
>
  <option value="UNPAID">Unpaid</option>
  <option value="PENDING_REVIEW">Pending Review</option>
  <option value="PAID">Paid</option>
  <option value="EXPIRED">Expired</option>
</select>

          </p>

          <div class="actions">
            <button class="details-btn" @click="openBookingDetails(booking)">
              View Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- No Bookings -->
    <div v-else-if="!loading && !bookings.length" class="no-data">
      No bookings found
    </div>

    <!-- DETAILS MODAL -->
    <div v-if="selectedBooking" class="modal-overlay">
      <div class="modal">
        <h2>{{ selectedBooking.propertyName }}</h2>

        <div class="details-section">
          <p><strong>Customer:</strong> {{ selectedBooking.customerName }}</p>
          <p><strong>Email:</strong> {{ selectedBooking.customerEmail }}</p>
          <p><strong>Phone:</strong> {{ selectedBooking.customerPhone }}</p>

          <p>
            <strong>Dates:</strong>
            {{ formatDate(selectedBooking.startDate) }} →
            {{ formatDate(selectedBooking.endDate) }}
          </p>

          <p><strong>Status:</strong> {{ selectedBooking.status }}</p>

          <!-- PAYMENT STATUS (MODAL) ✅ -->
          <p>
            <strong>Payment:</strong>
            <select
              v-model="selectedBooking.paymentStatus"
              class="status-select"
              :disabled="selectedBooking.paymentStatus === 'PAID'"
              @change="updatePaymentStatus(selectedBooking)"
            >
              <option value="UNPAID">Unpaid</option>
              <option value="PENDING">Pending</option>
              <option value="PAID">Paid</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </p>

          <p><strong>Total Price:</strong> {{ selectedBooking.totalPrice }}</p>
          <p><strong>Quantity:</strong> {{ selectedBooking.numberOfProperty }}</p>
        </div>

        <!-- Payment Proof -->
        <div class="payment-proof">
          <h3>Payment Proof</h3>
          <img
            v-if="selectedBooking.paymentProofPath"
            :src="getImageUrl(selectedBooking.paymentProofPath)"
            class="modal-img"
          />
          <p v-else class="text-gray">No payment proof uploaded</p>
        </div>

        <div class="modal-actions">
          <button
            class="delete-btn"
            @click="deleteBooking(selectedBooking.bookingId)"
          >
            Delete Booking
          </button>

          <button class="close-btn" @click="selectedBooking = null">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  'https://lmgtech-4.onrender.com/merchant'

const CLOUD_BASE_URL =
  import.meta.env.VITE_CLOUD_URL ||
  'https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload'

const token = localStorage.getItem('merchantToken')

const bookings = ref([])
const loading = ref(true)
const selectedBooking = ref(null)

/* ---------------- HELPERS ---------------- */

const getImageUrl = (url) => {
  if (!url) return ''
  return url.startsWith('http')
    ? url
    : `${CLOUD_BASE_URL}/${url.replace(/\\/g, '/')}`
}

const formatDate = (date) =>
  date ? new Date(date).toLocaleDateString() : '—'

/* ---------------- API ---------------- */

const fetchBookings = async () => {
  loading.value = true
  try {
    const res = await axios.get(
      `${API_BASE_URL}/operations/bookings`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    )
    bookings.value = res.data.bookings || []
  } catch (err) {
    console.error(err.response?.data || err.message)
  } finally {
    loading.value = false
  }
}

const updateBookingStatus = async (booking) => {
  const oldStatus = booking.status
  try {
    await axios.patch(
      `${API_BASE_URL}/operations/bookings/${booking.bookingId}/status`,
      { status: booking.status },
      { headers: { Authorization: `Bearer ${token}` } }
    )
  } catch (err) {
    booking.status = oldStatus
    alert('Failed to update booking status')
  }
}

/* ✅ PAYMENT STATUS UPDATE */
const updatePaymentStatus = async (booking) => {
  const oldStatus = booking.paymentStatus
  try {
    await axios.patch(
      `${API_BASE_URL}/operations/bookings/${booking.bookingId}/status`, // ✅ same endpoint as booking status
      { paymentStatus: booking.paymentStatus }, // send paymentStatus in body
      { headers: { Authorization: `Bearer ${token}` } }
    )
  } catch (err) {
    booking.paymentStatus = oldStatus
    alert('Failed to update payment status')
    console.error(err.response?.data || err.message)
  }
}

const deleteBooking = async (id) => {
  if (!confirm('Delete this booking?')) return
  try {
    await axios.delete(
      `${API_BASE_URL}/operations/bookings/${id}`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    bookings.value = bookings.value.filter(b => b.bookingId !== id)
    selectedBooking.value = null
  } catch (err) {
    alert('Failed to delete booking')
  }
}

const openBookingDetails = (booking) => {
  selectedBooking.value = booking
}

onMounted(fetchBookings)
</script>
<style scoped>
.booking-list-page {
  padding: 2rem;
  font-family: 'Inter', sans-serif;
}
.page-title {
  font-size: 1.8rem;
  color: #1e3a8a;
  font-weight: 700;
  margin-bottom: 1rem;
  text-align: center;
}
.bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.booking-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
  padding: 1rem;
}
.booking-card:hover { transform: translateY(-4px); }
.booking-info h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.status-select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  width: 100%;
}
.actions {
  margin-top: 0.6rem;
}
.details-btn {
  background-color: #2563eb;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
}
.details-btn:hover { opacity: 0.9; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}
.modal {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  width: 100%;
  max-width: 460px;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-img {
  width: 100%;
  border-radius: 8px;
  margin: 1rem 0;
}
.details-section {
  margin-bottom: 1rem;
}
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}
.delete-btn { background-color: #ef4444; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; width: 100%; }
.close-btn { background-color: #6b7280; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; width: 100%; }

.spinner {
  border: 3px solid #ddd;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-overlay { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 50vh; }
.no-data { text-align: center; margin-top: 2rem; font-size: 1.1rem; color: #6b7280; }

/* Responsive adjustments */
@media (max-width: 768px) {
  .bookings-grid { grid-template-columns: 1fr; }
  .booking-card { padding: 0.75rem; }
  .page-title { font-size: 1.5rem; }
  .status-select { font-size: 0.85rem; }
}
</style>
