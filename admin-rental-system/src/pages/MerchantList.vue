<template>
  <div class="merchant-list">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <p class="subtitle">{{ t('merchantList.subtitle') }}</p>
        <h1 class="title">{{ t('merchantList.title') }}</h1>
      </div>
      <button @click="fetchMerchants" class="refresh-btn">
        <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        {{ t('actions.refresh') }}
      </button>
    </div>

    <!-- Search Bar -->
    <div class="search-container">
      <div class="search-wrapper">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
        <input
          v-model="searchQuery"
          :placeholder="t('merchantList.searchPlaceholder')"
          class="search-input"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <div class="loader"></div>
      <p>{{ t('merchantList.loading') }}</p>
    </div>

    <!-- Merchant Table -->
    <div class="table-container">
      <table class="data-table">
        <thead class="table-header">
          <tr>
            <th class="table-th">#</th>
            <th class="table-th">{{ t('merchantList.name') }}</th>
            <th class="table-th">{{ t('merchantList.email') }}</th>
            <th class="table-th">{{ t('merchantList.phone') }}</th>
            <th class="table-th">{{ t('merchantList.businessName') }}</th>
            <th class="table-th">{{ t('merchantList.address') }}</th>
            <th class="table-th">{{ t('merchantList.status') }}</th>
            <th class="table-th text-center">{{ t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(merchant, index) in filteredMerchants"
            :key="merchant._id"
            class="table-row"
          >
            <td class="table-td">{{ index + 1 }}</td>
            <td class="table-td">{{ merchant.fullName }}</td>
            <td class="table-td">{{ merchant.email }}</td>
            <td class="table-td">{{ merchant.phonenumber || '-' }}</td>
            <td class="table-td">{{ merchant.businessName }}</td>
            <td class="table-td">{{ merchant.address }}</td>
            <td class="table-td">
              <span :class="merchant.isActive ? 'status-active' : 'status-suspended'">
                {{ merchant.isActive ? t('merchantList.active') : t('merchantList.suspended') }}
              </span>
            </td>
            <td class="table-td text-center">
              <div class="action-buttons">
                <button @click="openEditModal(merchant)" class="btn-edit">
                  <svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  {{ t('actions.edit') }}
                </button>
                <button @click="openConfirmModal('toggle', merchant)" :class="merchant.isActive ? 'btn-suspend' : 'btn-unsuspend'">
                  {{ merchant.isActive ? t('actions.suspend') : t('actions.unsuspend') }}
                </button>
                <button @click="openConfirmModal('delete', merchant)" class="btn-delete">
                  <svg class="icon-xs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                  {{ t('actions.delete') }}
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="!filteredMerchants.length" class="empty-row">
            <td colspan="8" class="empty-cell">
              {{ t('merchantList.empty') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Merchant Button -->
    <div class="add-button-container">
      <button @click="openAddModal" class="add-btn">
        <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        {{ t('merchant.add') }}
      </button>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddMerchant || showEditMerchant"
      class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
    >
      <div class="bg-white dark:bg-slate-900 p-6 rounded-lg w-full max-w-2xl relative">
        <button
          @click="closeAddEditModal"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:hover:text-white font-bold text-lg"
        >
          ✕
        </button>

        <h2 class="text-2xl font-extrabold text-center text-blue-700 dark:text-blue-400 mb-3">
          {{ showEditMerchant ? t('merchant.edit') : t('merchant.add') }}
        </h2>
        <p class="text-center text-gray-500 dark:text-gray-400 mb-6">
          {{ showEditMerchant ? t('merchant.editSubtitle') : t('merchant.addSubtitle') }}
        </p>

        <form @submit.prevent="submitAddEditMerchant" enctype="multipart/form-data" class="flex flex-col gap-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input v-model="form.fullName" type="text" :placeholder="t('merchant.fullNamePlaceholder')" class="form-input" required />
            <input v-model="form.email" type="email" :placeholder="t('merchant.emailPlaceholder')" class="form-input" required />

            <!-- Password Field with Show/Hide -->
            <div class="password-wrapper">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('merchant.passwordPlaceholder')"
                class="form-input"
                :required="!showEditMerchant"
              />
              <button type="button" @click="togglePassword" class="password-toggle-btn">
                {{ showPassword ? t('actions.hide') : t('actions.show') }}
              </button>
            </div>

            <input v-model="form.phonenumber" type="text" :placeholder="t('merchant.phonePlaceholder')" class="form-input" required />
            <input v-model="form.businessName" type="text" :placeholder="t('merchant.businessNamePlaceholder')" class="form-input" required />
            <input v-model="form.address" type="text" :placeholder="t('merchant.addressPlaceholder')" class="form-input" required />
            <input v-model="form.acountnumber" type="text" :placeholder="t('merchant.accountNumberPlaceholder')" class="form-input" required />
            <input type="file" @change="handleFileUpload" class="col-span-1 md:col-span-2" accept="image/*" />
          </div>

          <button type="submit" :disabled="loading" class="btn-submit mt-2">
            <span v-if="loading" class="loader-spinner"></span>
            {{ loading ? t('merchant.loading') : showEditMerchant ? t('merchant.edit') : t('merchant.submit') }}
          </button>

          <p v-if="message" :class="[isError ? 'text-red-600' : 'text-green-600', 'text-center mt-2 font-semibold']">
            {{ message }}
          </p>
        </form>
      </div>
    </div>

    <!-- Confirm Modal -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div class="bg-white rounded-lg shadow-lg p-4 w-80 dark:bg-gray-800">
        <h3 class="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-100">
          {{ modalAction === 'delete' ? t('modal.deleteTitle') : t('modal.changeStatusTitle') }}
        </h3>
        <p class="text-gray-600 dark:text-gray-300 mb-4 text-sm">
          {{ t('modal.confirmText', { action: modalAction === 'delete' ? t('actions.delete') : merchantToActOn?.isActive ? t('actions.suspend') : t('actions.unsuspend') }) }}
        </p>
        <div class="flex justify-end gap-2">
          <button @click="closeModal" class="px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm">
            {{ t('actions.cancel') }}
          </button>
          <button @click="confirmAction" class="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">
            {{ t('actions.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const merchants = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showModal = ref(false)
const modalAction = ref('')
const merchantToActOn = ref(null)
const showAddMerchant = ref(false)
const showEditMerchant = ref(false)

const form = ref({
  _id: '',
  fullName: '',
  email: '',
  password: '',
  phonenumber: '',
  acountnumber: '',
  businessName: '',
  address: '',
  profilePictureFile: null,
})

const message = ref('')
const isError = ref(false)
const showPassword = ref(false)
const togglePassword = () => (showPassword.value = !showPassword.value)
const handleFileUpload = (e) => { form.value.profilePictureFile = e.target.files[0] }

const fetchMerchants = async () => {
  loading.value = true
  message.value = ''
  isError.value = false

  try {
    const token = localStorage.getItem('adminToken')
    const { data } = await axios.get('https://lmgtech-4.onrender.com/merchant/all', {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (Array.isArray(data)) {
      merchants.value = data
    } else if (Array.isArray(data.merchants)) {
      merchants.value = data.merchants
    } else if (Array.isArray(data.data)) {
      merchants.value = data.data
    } else {
      merchants.value = data || []
    }
  } catch (err) {
    console.error('Failed to fetch merchants:', err)
    message.value = err.response?.data?.message || 'Failed to load merchants.'
    isError.value = true
  } finally {
    loading.value = false
  }
}

const openConfirmModal = (action, merchant) => {
  modalAction.value = action
  merchantToActOn.value = merchant
  showModal.value = true
}
const closeModal = () => {
  showModal.value = false
  merchantToActOn.value = null
  modalAction.value = ''
}

const openAddModal = () => {
  showAddMerchant.value = true
  showEditMerchant.value = false
  resetForm()
}
const openEditModal = (merchant) => {
  showEditMerchant.value = true
  showAddMerchant.value = false
  Object.assign(form.value, merchant)
  form.value.password = ''
}
const closeAddEditModal = () => {
  showAddMerchant.value = false
  showEditMerchant.value = false
  resetForm()
}
const resetForm = () => {
  form.value = { _id:'', fullName:'', email:'', password:'', phonenumber:'', acountnumber:'', businessName:'', address:'', profilePictureFile:null }
  message.value = ''
  isError.value = false
}

const submitAddEditMerchant = async () => {
  loading.value = true
  message.value = ''
  isError.value = false

  try {
    const formData = new FormData()
    formData.append('fullName', form.value.fullName)
    formData.append('email', form.value.email)
    if (!showEditMerchant.value && form.value.password) formData.append('password', form.value.password)
    formData.append('phonenumber', form.value.phonenumber)
    formData.append('acountnumber', form.value.acountnumber)
    formData.append('businessName', form.value.businessName)
    formData.append('address', form.value.address)
    if (form.value.profilePictureFile) formData.append('profilePictureFile', form.value.profilePictureFile)

    const token = localStorage.getItem('adminToken')
    let response
    if (showEditMerchant.value) {
      response = await axios.put(`https://lmgtech-4.onrender.com/merchant/admin/update/${form.value._id}`, formData, { headers: { Authorization: `Bearer ${token}`, 'accept-language': locale.value } })
    } else {
      response = await axios.post('https://lmgtech-4.onrender.com/merchant/register', formData, { headers: { Authorization: `Bearer ${token}`, 'accept-language': locale.value } })
    }

    message.value = response.data.message || (showEditMerchant.value ? t('merchant.updated') : t('merchant.success'))
    await fetchMerchants()
    closeAddEditModal()
  } catch (err) {
    console.error(err)
    message.value = err.response?.data?.message || t('merchant.failed')
    isError.value = true
  } finally {
    loading.value = false
  }
}

const confirmAction = async () => {
  if (!merchantToActOn.value) return
  const token = localStorage.getItem('adminToken')
  try {
    if (modalAction.value === 'delete') {
      await axios.delete(`https://lmgtech-4.onrender.com/merchant/${merchantToActOn.value._id}`, { headers: { Authorization: `Bearer ${token}` } })
      merchants.value = merchants.value.filter(m => m._id !== merchantToActOn.value._id)
    } else if (modalAction.value === 'toggle') {
      const updated = { isActive: !merchantToActOn.value.isActive }
      await axios.put(`https://lmgtech-4.onrender.com/merchant/admin/update/${merchantToActOn.value._id}`, updated, { headers: { Authorization: `Bearer ${token}` } })
      merchantToActOn.value.isActive = !merchantToActOn.value.isActive
    }
  } catch (err) {
    console.error(err)
  } finally {
    closeModal()
  }
}

const filteredMerchants = computed(() => {
  const currentMerchants = Array.isArray(merchants.value) ? merchants.value : []
  if (!searchQuery.value.trim()) return currentMerchants
  const q = searchQuery.value.toLowerCase()
  return currentMerchants.filter(
    m => m.fullName?.toLowerCase().includes(q) ||
         m.email?.toLowerCase().includes(q) ||
         m.businessName?.toLowerCase().includes(q)
  )
})

onMounted(fetchMerchants)
</script>

<style scoped>
/* ===== BASE LAYOUT ===== */
.merchant-list {
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
}
.dark .merchant-list {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

/* ===== HEADER ===== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  gap: 16px;
}
.header-content {
  flex: 1;
}
.title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
  color: #1f2937;
}
.dark .title {
  color: #f9fafb;
}
.subtitle {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6b7280;
  margin: 0;
}
.dark .subtitle {
  color: #9ca3af;
}
.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

/* ===== SEARCH ===== */
.search-container {
  margin-bottom: 24px;
}
.search-wrapper {
  position: relative;
  max-width: 400px;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #6b7280;
}
.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.dark .search-input {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}
.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* ===== LOADING ===== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #6b7280;
}
.dark .loading-container {
  color: #9ca3af;
}

/* ===== TABLE ===== */
.table-container {
  background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}
.dark .table-container {
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
  border-color: #4b5563;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.table-header {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}
.dark .table-header {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
}
.table-th {
  padding: 16px 20px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}
.dark .table-th {
  color: #f9fafb;
  border-bottom-color: #4b5563;
}
.table-row {
  transition: all 0.2s ease;
}
.table-row:hover {
  background: rgba(59, 130, 246, 0.05);
}
.dark .table-row:hover {
  background: rgba(59, 130, 246, 0.1);
}
.table-td {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  color: #374151;
}
.dark .table-td {
  border-bottom-color: #4b5563;
  color: #f9fafb;
}
.status-active {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}
.dark .status-active {
  background: #14532d;
  color: #bbf7d0;
  border-color: #166534;
}
.status-suspended {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}
.dark .status-suspended {
  background: #7f1d1d;
  color: #fca5a5;
  border-color: #991b1b;
}
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}
.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.btn-suspend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-suspend:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}
.btn-unsuspend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-unsuspend:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.btn-delete {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}
.empty-row {
  text-align: center;
}
.empty-cell {
  padding: 48px;
  color: #6b7280;
}
.dark .empty-cell {
  color: #9ca3af;
}

/* ===== ADD BUTTON ===== */
.add-button-container {
  text-align: right;
}
.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(31, 41, 55, 0.3);
}
.dark .add-btn {
  background: linear-gradient(135deg, #f9fafb 0%, #e5e7eb 100%);
  color: #1f2937;
}
.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(31, 41, 55, 0.4);
}
.dark .add-btn:hover {
  box-shadow: 0 8px 20px rgba(249, 250, 251, 0.2);
}

/* ===== ICONS ===== */
.icon-sm {
  width: 16px;
  height: 16px;
}
.icon-xs {
  width: 14px;
  height: 14px;
}

/* ===== LOADER ===== */
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
.dark .loader {
  border-color: #4b5563;
  border-top-color: #3b82f6;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .merchant-list {
    padding: 16px;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  .title {
    font-size: 24px;
  }
  .table-th, .table-td {
    padding: 12px 8px;
    font-size: 12px;
  }
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-edit, .btn-suspend, .btn-unsuspend, .btn-delete {
    justify-content: center;
  }
}
</style>
