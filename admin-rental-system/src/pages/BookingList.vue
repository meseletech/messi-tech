<template>
  <div class="wrap">
    <div class="hero">
      <div>
        <p class="eyebrow">Operations</p>
        <h1 class="heading">{{ $t('bookingList.title') }}</h1>
      </div>
      <div class="stats">
        <div class="stat-chip">
          <span class="stat-label">Total</span>
          <strong>{{ bookings.length }}</strong>
        </div>
        <div class="stat-chip">
          <span class="stat-label">Visible</span>
          <strong>{{ filteredBookings.length }}</strong>
        </div>
      </div>
    </div>

    <div class="controls-card">
      <div class="controls">
        <input v-model="search" :placeholder="$t('bookings.searchPlaceholder')" class="input" />
        <select v-model="statusFilter" class="input status-filter">
          <option value="">{{ $t('bookings.statusFilter.all') }}</option>
          <option value="PENDING">Pending</option>
          <option value="ACCEPTED">Accepted</option>
          <option value="DECLINED">Declined</option>
          <option value="CONFIRMED">Confirmed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
        <button @click="fetchBookings" class="btn">{{ $t('bookings.refresh') }}</button>
      </div>
    </div>

    <div v-if="loading" class="meta">{{ $t('bookings.loading') }}</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- TABLE VIEW FOR DESKTOP -->
    <div v-if="!loading && bookings.length" class="table-wrap desktop-table">
      <table class="table">
        <thead>
          <tr>
            <th>#</th>
            <th>{{ $t('bookings.table.property') }}</th>
            <th>{{ $t('bookings.table.merchant') }}</th>
            <th>{{ $t('bookings.table.dates') }}</th>
            <th>{{ $t('bookings.table.payment') }}</th>
            <th>{{ $t('bookings.table.status') }}</th>
            <th>{{ $t('bookings.table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(b, idx) in filteredBookings" :key="getId(b)">
            <td class="cell">{{ idx + 1 }}</td>
            <td class="cell">
              <div class="prop">
                <img v-if="b.imageUrls?.length" :src="b.imageUrls[0]" class="thumb" />
                <div>
                  <div class="prop-name">{{ b.propertyName || b.assetName || $t('bookings.table.na') }}</div>
                  <div class="small">{{ $t('merchantList.category') || 'Category' }}: {{ b.category || $t('bookings.table.na') }}</div>
                </div>
              </div>
            </td>
            <td class="cell">
              <div>{{ b.merchant?.name || b.businessName || $t('bookings.table.na') }}</div>
              <div class="small">{{ b.merchant?.email || b.merchantEmail || '' }}</div>
            </td>
            <td class="cell">
              <div>{{ formatDate(b.startDate) }}</div>
              <div class="small">→ {{ formatDate(b.endDate) }}</div>
            </td>
            <td class="cell">
              <a v-if="b.paymentProofPath && b.paymentProofPath !== 'no payment proven'" :href="b.paymentProofPath" target="_blank">
                {{ $t('bookings.table.viewPayment') }}
              </a>
              <span v-else>{{ $t('bookings.table.na') }}</span>
            </td>
            <td class="cell">
              <select v-model="b.status" @change="onStatusChange(b)" class="input-small">
                <option value="PENDING">Pending</option>
                <option value="ACCEPTED">Accepted</option>
                <option value="DECLINED">Declined</option>
                <option value="CONFIRMED">Confirmed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </td>
            <td class="cell actions-cell">
              <button @click="openUpdate(b)" class="btn">{{ $t('bookings.table.update') }}</button>
              <button @click="confirmDelete(b)" class="btn-danger">{{ $t('bookings.table.delete') }}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MOBILE CARD VIEW -->
    <div v-if="!loading && bookings.length" class="mobile-cards">
      <div v-for="b in filteredBookings" :key="getId(b)" class="card">
        <div class="card-header">
          <img v-if="b.imageUrls?.length" :src="b.imageUrls[0]" class="thumb" />
          <div>
            <div class="prop-name">{{ b.propertyName || b.assetName || $t('bookings.table.na') }}</div>
            <div class="small">{{ $t('merchantList.category') || 'Category' }}: {{ b.category || $t('bookings.table.na') }}</div>
          </div>
        </div>
        <div class="card-body">
          <div><strong>{{ $t('bookings.table.merchant') }}:</strong> {{ b.merchant?.name || b.businessName || $t('bookings.table.na') }}</div>
          <div class="small">{{ b.merchant?.email || b.merchantEmail || '' }}</div>
          <div><strong>{{ $t('bookings.table.dates') }}:</strong> {{ formatDate(b.startDate) }} → {{ formatDate(b.endDate) }}</div>
          <div><strong>{{ $t('bookings.table.payment') }}:</strong>
            <a v-if="b.paymentProofPath && b.paymentProofPath !== 'no payment proven'" :href="b.paymentProofPath" target="_blank">
              {{ $t('bookings.table.viewPayment') }}
            </a>
            <span v-else>{{ $t('bookings.table.na') }}</span>
          </div>
          <div><strong>{{ $t('bookings.table.status') }}:</strong>
            <select v-model="b.status" @change="onStatusChange(b)" class="input-small">
              <option value="PENDING">Pending</option>
              <option value="ACCEPTED">Accepted</option>
              <option value="DECLINED">Declined</option>
              <option value="CONFIRMED">Confirmed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div class="card-actions">
            <button @click="openUpdate(b)" class="btn">{{ $t('bookings.table.update') }}</button>
            <button @click="confirmDelete(b)" class="btn-danger">{{ $t('bookings.table.delete') }}</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !bookings.length" class="meta">{{ $t('bookings.noBookings') }}</div>

    <!-- UPDATE MODAL -->
    <div v-if="showUpdateForm" class="modal-overlay" @click.self="cancelUpdate">
      <div class="modal">
        <h3>{{ $t('bookings.updateBooking') }}</h3>
        <div class="form-group">
          <label>{{ $t('bookings.table.status') }}</label>
          <select v-model="updateBooking.status" class="input-small">
            <option value="PENDING">Pending</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="DECLINED">Declined</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t('bookings.table.dates') }}</label>
          <div class="date-group">
            <input type="date" v-model="updateBooking.startDate" class="input" />
            <span>→</span>
            <input type="date" v-model="updateBooking.endDate" class="input" />
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('bookings.table.paymentProof') }}</label>
          <input type="text" v-model="updateBooking.paymentProofPath" class="input" placeholder="Payment URL or path" />
        </div>
        <div class="form-actions">
          <button @click="submitUpdate" class="btn">{{ $t('bookings.update') }}</button>
          <button @click="cancelUpdate" class="btn-danger">{{ $t('bookings.cancel') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAllBookings, updateBookingByAdmin, deleteBookingByAdmin } from '@/utils/booking.js';

export default {
  name: 'BookingList',
  data() {
    return {
      bookings: [],
      loading: false,
      error: null,
      search: '',
      statusFilter: '',
      updateBooking: null,
      showUpdateForm: false
    };
  },
  computed: {
    filteredBookings() {
      const q = this.search.trim().toLowerCase();
      return this.bookings.filter(b => {
        const name = (b.propertyName || b.assetName || '').toString().toLowerCase();
        const statusMatch = this.statusFilter ? (b.status === this.statusFilter) : true;
        const searchMatch = q ? name.includes(q) : true;
        return statusMatch && searchMatch;
      });
    },
  },
  methods: {
    getId(item) { return item._id || item.bookingId || item.id || null; },
    formatDate(dateStr) { return dateStr ? new Date(dateStr).toLocaleDateString() : this.$t('bookings.table.na'); },
    async fetchBookings() {
      this.loading = true;
      this.error = null;
      try {
        const res = await getAllBookings();
        let payload = res?.data;
        if (Array.isArray(payload)) this.bookings = payload;
        else if (payload && Array.isArray(payload.bookings)) this.bookings = payload.bookings;
        else if (payload && payload.data && Array.isArray(payload.data.bookings)) this.bookings = payload.data.bookings;
        else this.bookings = Array.isArray(payload) ? payload : (payload?.bookings || payload?.data?.bookings || []);

        this.bookings = this.bookings.map(b => ({
          ...b,
          _id: b.bookingId || b._id || b.id,
          status: b.status || 'PENDING',
          _previousStatus: b.status || 'PENDING',
        }));
      } catch (err) {
        console.error('Fetch bookings error:', err);
        this.error = err?.response?.data?.message || err.message || this.$t('bookings.updateFailed');
        this.bookings = [];
      } finally { this.loading = false; }
    },
    async onStatusChange(booking) {
      const id = this.getId(booking);
      if (!id) return alert(this.$t('bookings.alerts.missingId'));
      const previousStatus = booking._previousStatus || 'PENDING';
      try {
        await updateBookingByAdmin(id, { status: booking.status });
        booking._previousStatus = booking.status;
        alert(this.$t('bookings.alerts.statusUpdated'));
      } catch (err) {
        console.error('Error updating booking:', err);
        alert(err?.response?.data?.message || this.$t('bookings.alerts.updateFailed'));
        booking.status = previousStatus;
      }
    },
    confirmDelete(booking) {
      const bookingId = this.getId(booking);
      if (!bookingId) return alert(this.$t('bookings.alerts.missingId'));
      if (!confirm(this.$t('bookings.alerts.deleteConfirm'))) return;
      this.removeBooking(bookingId);
    },
    async removeBooking(bookingId) {
      try {
        await deleteBookingByAdmin(bookingId);
        this.bookings = this.bookings.filter(b => this.getId(b) !== bookingId);
        alert(this.$t('bookings.alerts.statusUpdated'));
      } catch (err) {
        console.error('Error deleting booking:', err);
        alert(err?.response?.data?.message || this.$t('bookings.alerts.deleteFailed'));
      }
    },
    openUpdate(booking) {
      this.updateBooking = { ...booking };
      this.showUpdateForm = true;
    },
    async submitUpdate() {
      if (!this.updateBooking) return;
      const id = this.getId(this.updateBooking);
      try {
        await updateBookingByAdmin(id, {
          status: this.updateBooking.status,
          startDate: this.updateBooking.startDate,
          endDate: this.updateBooking.endDate,
          paymentProofPath: this.updateBooking.paymentProofPath,
        });
        const index = this.bookings.findIndex(b => this.getId(b) === id);
        if (index !== -1) this.bookings[index] = { ...this.bookings[index], ...this.updateBooking };
        alert(this.$t('bookings.alerts.statusUpdated'));
        this.showUpdateForm = false;
        this.updateBooking = null;
      } catch (err) {
        console.error('Update booking error:', err);
        alert(err?.response?.data?.message || this.$t('bookings.alerts.updateFailed'));
      }
    },
    cancelUpdate() {
      this.showUpdateForm = false;
      this.updateBooking = null;
    }
  },
  mounted() { this.fetchBookings(); },
};
</script>
<style scoped>
.wrap {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  color: #102a43;
  background:
    radial-gradient(circle at 0% 0%, rgba(21, 101, 192, 0.08), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(55, 148, 110, 0.08), transparent 42%);
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
  color: #486581;
  font-weight: 700;
}

.heading {
  margin: 4px 0 0;
  font-size: clamp(1.4rem, 2.2vw, 2rem);
  font-weight: 800;
}

.stats {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-chip {
  min-width: 120px;
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  padding: 10px 12px;
  box-shadow: 0 10px 24px rgba(16, 42, 67, 0.06);
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #627d98;
}

.controls-card {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  box-shadow: 0 12px 28px rgba(16, 42, 67, 0.06);
  padding: 12px;
  margin-bottom: 14px;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.input,
.input-small {
  border: 1px solid #bcccdc;
  background: #fff;
  color: #102a43;
  border-radius: 10px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input {
  min-width: 180px;
  padding: 10px 12px;
  flex: 1 1 260px;
}

.status-filter {
  flex: 0 0 210px;
}

.input-small {
  min-width: 140px;
  padding: 8px 10px;
}

.input:focus,
.input-small:focus {
  outline: none;
  border-color: #1565c0;
  box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.16);
}

.btn,
.btn-danger {
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn {
  padding: 10px 14px;
  color: #fff;
  background: linear-gradient(135deg, #1565c0, #0d47a1);
  box-shadow: 0 8px 16px rgba(13, 71, 161, 0.3);
}

.btn-danger {
  padding: 8px 12px;
  color: #fff;
  background: linear-gradient(135deg, #d32f2f, #b71c1c);
  box-shadow: 0 8px 16px rgba(183, 28, 28, 0.28);
}

.btn:hover,
.btn-danger:hover {
  transform: translateY(-1px);
}

.meta {
  margin: 10px 0;
  color: #486581;
}

.error {
  color: #b00020;
  margin: 10px 0;
  font-weight: 700;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 14px 28px rgba(16, 42, 67, 0.08);
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 960px;
}

.table th {
  padding: 12px;
  text-align: left;
  font-size: 12px;
  color: #334e68;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: #f0f4f8;
  border-bottom: 1px solid #d9e2ec;
}

.table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
}

.table tbody tr:hover {
  background: #f8fbff;
}

.prop {
  display: flex;
  gap: 10px;
  align-items: center;
}

.thumb {
  width: 64px;
  height: 52px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #d9e2ec;
}

.prop-name {
  font-weight: 700;
}

.small {
  font-size: 12px;
  color: #627d98;
}

.actions-cell {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mobile-cards {
  display: none;
}

.card {
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 12px;
  background: #fff;
  box-shadow: 0 10px 22px rgba(16, 42, 67, 0.06);
}

.card-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #243b53;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 28, 44, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 12px;
}

.modal {
  background: #fff;
  padding: 22px;
  border-radius: 14px;
  width: 460px;
  max-width: 100%;
  box-shadow: 0 24px 36px rgba(12, 28, 44, 0.24);
}

.modal h3 {
  margin: 0 0 16px;
  font-size: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
  gap: 6px;
}

.date-group {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 14px;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: block;
  }
}

@media (max-width: 768px) {
  .wrap {
    padding: 16px;
  }

  .controls {
    flex-direction: column;
  }

  .input,
  .status-filter,
  .input-small {
    width: 100%;
    min-width: 0;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-actions button {
    flex: 1 1 48%;
  }

  .modal {
    width: 95%;
  }
}

@media (max-width: 480px) {
  .card-actions button {
    flex: 1 1 100%;
  }
}
</style>