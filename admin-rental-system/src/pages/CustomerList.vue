<template>
  <div class="container">
    <div class="hero">
      <div>
        <p class="eyebrow">Customer Management</p>
        <h2>{{ t('customer.listTitle') }}</h2>
      </div>
      <div class="hero-actions">
        <div class="stat-chip">
          <span>Total</span>
          <strong>{{ customers.length }}</strong>
        </div>
        <div class="stat-chip">
          <span>Active</span>
          <strong>{{ activeCount }}</strong>
        </div>
        <button class="btn btn-refresh" @click="fetchCustomers">
          {{ t('actions.refresh') }}
        </button>
      </div>
    </div>

    <div class="search-container">
      <input
        v-model="searchQuery"
        :placeholder="t('customer.searchPlaceholder')"
        class="search-input"
      />
    </div>

    <div v-if="loading" class="loading">Loading customers...</div>

    <div class="table-wrapper desktop-table">
      <table class="customer-table">
        <thead>
          <tr>
            <th>{{ t('customer.name') }}</th>
            <th>{{ t('customer.email') }}</th>
            <th>{{ t('customer.phone') }}</th>
            <th>{{ t('customer.address') }}</th>
            <th>{{ t('customer.status') }}</th>
            <th>{{ t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in filteredCustomers" :key="customer.id">
            <td>{{ customer.fullName }}</td>
            <td>{{ customer.email }}</td>
            <td>{{ customer.phonenumber }}</td>
            <td>{{ customer.address }}</td>
            <td>
              <span :class="['status', customer.isActive ? 'active' : 'suspended']">
                {{ customer.isActive ? t('customer.active') : t('customer.suspended') }}
              </span>
            </td>
            <td class="actions">
              <button :class="['btn', customer.isActive ? 'btn-warning' : 'btn-success']"
                      @click="openConfirm(customer, 'toggle')">
                {{ customer.isActive ? t('actions.suspend') : t('actions.unsuspend') }}
              </button>
              <button class="btn btn-edit" @click="openEditModal(customer)">
                {{ t('actions.edit') }}
              </button>
              <button class="btn btn-danger" @click="openConfirm(customer, 'delete')">
                {{ t('actions.delete') }}
              </button>
            </td>
          </tr>
          <tr v-if="!filteredCustomers.length">
            <td colspan="6" class="empty-state">
              {{ t('customer.empty') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mobile-cards">
      <div v-for="customer in filteredCustomers" :key="customer.id" class="card">
        <div class="card-header">
          <div class="name">{{ customer.fullName }}</div>
          <div class="status" :class="customer.isActive ? 'active' : 'suspended'">
            {{ customer.isActive ? t('customer.active') : t('customer.suspended') }}
          </div>
        </div>
        <div class="card-body">
          <div><strong>{{ t('customer.email') }}:</strong> {{ customer.email }}</div>
          <div><strong>{{ t('customer.phone') }}:</strong> {{ customer.phonenumber }}</div>
          <div><strong>{{ t('customer.address') }}:</strong> {{ customer.address }}</div>
          <div class="card-actions">
            <button :class="['btn', customer.isActive ? 'btn-warning' : 'btn-success']"
                    @click="openConfirm(customer, 'toggle')">
              {{ customer.isActive ? t('actions.suspend') : t('actions.unsuspend') }}
            </button>
            <button class="btn btn-edit" @click="openEditModal(customer)">
              {{ t('actions.edit') }}
            </button>
            <button class="btn btn-danger" @click="openConfirm(customer, 'delete')">
              {{ t('actions.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showConfirm" class="modal-backdrop">
      <div class="modal">
        <h3>{{ confirmActionType === 'delete' ? 'Confirm Deletion' : 'Confirm Status Change' }}</h3>
        <p>
          Are you sure you want to
          {{ confirmActionType === 'delete' ? 'delete' : selectedCustomer?.isActive ? 'suspend' : 'unsuspend' }}
          <strong>{{ selectedCustomer?.fullName }}</strong>?
        </p>
        <div class="modal-actions">
          <button class="btn btn-cancel" @click="showConfirm=false">Cancel</button>
          <button class="btn btn-confirm" @click="confirmAction">Confirm</button>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-backdrop">
      <div class="modal">
        <h3>Edit Customer</h3>
        <form @submit.prevent="submitEdit">
          <label>Full Name</label>
          <input v-model="editCustomerData.fullName" required />

          <label>Email</label>
          <input v-model="editCustomerData.email" type="email" required />

          <label>Phone</label>
          <input v-model="editCustomerData.phonenumber" required />

          <label>Address</label>
          <input v-model="editCustomerData.address" required />

          <div class="modal-actions">
            <button type="button" class="btn btn-cancel" @click="showEditModal=false">Cancel</button>
            <button type="submit" class="btn btn-confirm">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const customers = ref([])
const searchQuery = ref('')
const loading = ref(false)

const showConfirm = ref(false)
const selectedCustomer = ref(null)
const confirmActionType = ref('')

const showEditModal = ref(false)
const editCustomerData = ref({})

const token = localStorage.getItem('adminToken')

const fetchCustomers = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('https://lmgtech-e1q0.onrender.com/customer/all', {
      headers: { Authorization: `Bearer ${token}` },
    })
    customers.value = data.customers || []
  } catch (err) {
    console.error(err)
    alert('Failed to fetch customers.')
  } finally {
    loading.value = false
  }
}

const filteredCustomers = computed(() => {
  if (!searchQuery.value.trim()) return customers.value
  return customers.value.filter(
    c =>
      (c.fullName || '').toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (c.email || '').toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const activeCount = computed(() => customers.value.filter(c => c.isActive).length)

const openConfirm = (customer, actionType) => {
  selectedCustomer.value = customer
  confirmActionType.value = actionType
  showConfirm.value = true
}

const confirmAction = async () => {
  if (!selectedCustomer.value) return
  try {
    if (confirmActionType.value === 'delete') {
      await axios.delete(`https://lmgtech-e1q0.onrender.com/customer/${selectedCustomer.value.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      customers.value = customers.value.filter(c => c.id !== selectedCustomer.value.id)
      alert('Customer deleted!')
    } else if (confirmActionType.value === 'toggle') {
      const updatedStatus = { isActive: !selectedCustomer.value.isActive }
      await axios.patch(`https://lmgtech-e1q0.onrender.com/customer/admin/customers/${selectedCustomer.value.id}`, updatedStatus, {
        headers: { Authorization: `Bearer ${token}` },
      })
      selectedCustomer.value.isActive = !selectedCustomer.value.isActive
      alert('Status updated!')
    }
  } catch (err) {
    console.error(err)
    alert('Operation failed.')
  }
  showConfirm.value = false
  selectedCustomer.value = null
}

const openEditModal = (customer) => {
  editCustomerData.value = { ...customer }
  showEditModal.value = true
}

const submitEdit = async () => {
  try {
    const { id, fullName, email, phonenumber, address } = editCustomerData.value
    const updated = { fullName, email, phonenumber, address }
    await axios.patch(`https://lmgtech-e1q0.onrender.com/customer/admin/customers/${id}`, updated, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const index = customers.value.findIndex(c => c.id === id)
    if (index !== -1) customers.value[index] = { ...customers.value[index], ...updated }
    alert('Customer updated!')
    showEditModal.value = false
  } catch (err) {
    console.error(err)
    alert('Failed to update customer.')
  }
}

onMounted(fetchCustomers)
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: auto;
  padding: 24px;
  color: #102a43;
  background:
    radial-gradient(circle at 100% 0%, rgba(12, 88, 166, 0.1), transparent 38%),
    radial-gradient(circle at 0% 100%, rgba(39, 145, 104, 0.08), transparent 38%);
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 18px;
}

.hero h2 {
  margin: 4px 0 0;
  font-size: clamp(1.4rem, 2vw, 2rem);
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #486581;
  font-weight: 700;
}

.hero-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.stat-chip {
  min-width: 108px;
  padding: 8px 12px;
  border-radius: 12px;
  border: 1px solid #d9e2ec;
  background: #fff;
  box-shadow: 0 10px 20px rgba(16, 42, 67, 0.07);
}

.stat-chip span {
  display: block;
  color: #627d98;
  font-size: 12px;
}

.btn {
  cursor: pointer;
  padding: 8px 12px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-refresh {
  background: linear-gradient(135deg, #1565c0, #0d47a1);
  color: #fff;
  box-shadow: 0 10px 18px rgba(13, 71, 161, 0.28);
}

.btn-edit {
  background-color: #1565c0;
  color: #fff;
}

.btn-success {
  background-color: #1d7a46;
  color: #fff;
}

.btn-warning {
  background-color: #d28d02;
  color: #fff;
}

.btn-danger {
  background-color: #c12f2f;
  color: #fff;
}

.btn-cancel {
  background-color: #f0f4f8;
  color: #243b53;
}

.btn-confirm {
  background-color: #0f609b;
  color: #fff;
}

.search-container {
  margin-bottom: 14px;
}

.search-input {
  width: 100%;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid #bcccdc;
  background: #fff;
  color: #102a43;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.loading {
  margin-bottom: 12px;
  color: #486581;
  font-weight: 600;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 14px 28px rgba(16, 42, 67, 0.08);
}

.customer-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 780px;
}

.customer-table th,
.customer-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #edf2f7;
}

.customer-table th {
  background-color: #f0f4f8;
  color: #334e68;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
}

.customer-table tr:hover {
  background-color: #f8fbff;
}

.status {
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.status.active {
  background-color: #e3f9ec;
  color: #166534;
}

.status.suspended {
  background-color: #fee9e9;
  color: #9b1c1c;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: #627d98;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(12, 28, 44, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
}
.modal {
  background-color: #fff;
  color: #102a43;
  padding: 24px;
  border-radius: 16px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 24px 36px rgba(12, 28, 44, 0.24);
}

.modal h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 14px;
}

.modal p {
  margin-bottom: 20px;
}

.modal input {
  width: 100%;
  margin-bottom: 10px;
  border: 1px solid #bcccdc;
  border-radius: 10px;
  padding: 9px 10px;
}

.modal input:focus {
  outline: none;
  border-color: #1565c0;
  box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.16);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.mobile-cards {
  display: none;
}

.card {
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  background: #fff;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 10px 20px rgba(16, 42, 67, 0.06);
}

.card .name {
  font-weight: 700;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .container {
    padding: 16px;
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .desktop-table { display: none; }
  .mobile-cards { display: block; }

  .card-actions button {
    flex: 1 1 auto;
    max-width: 140px;
    padding: 6px 8px;
    font-size: 13px;
  }

  .card-header { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 480px) {
  .card-actions button {
    flex: 1 1 100%;
    max-width: 100%;
  }
}

</style>
