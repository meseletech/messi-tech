<template>
  <div class="merchant-list">
    <div class="header">
      <div class="header-content">
        <p class="subtitle">Merchant Operations</p>
        <h1 class="title">{{ t('merchantList.title') }}</h1>
      </div>
      <div class="header-actions">
        <div class="summary-chip">
          <span>Total</span>
          <strong>{{ filteredMerchants.length }}</strong>
        </div>
        <div class="summary-chip">
          <span>Active</span>
          <strong>{{ activeMerchants }}</strong>
        </div>
        <button @click="fetchMerchants" class="refresh-btn">
          <svg class="icon-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          {{ t('actions.refresh') }}
        </button>
      </div>
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

    <div class="table-container desktop-table">
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

    <div class="mobile-cards">
      <div
        v-for="merchant in filteredMerchants"
        :key="merchant._id"
        class="merchant-card"
      >
        <div class="merchant-card-head">
          <div>
            <div class="card-title">{{ merchant.fullName }}</div>
            <div class="card-subtitle">{{ merchant.businessName }}</div>
          </div>
          <span :class="merchant.isActive ? 'status-active' : 'status-suspended'">
            {{ merchant.isActive ? t('merchantList.active') : t('merchantList.suspended') }}
          </span>
        </div>
        <div class="merchant-card-body">
          <div><strong>{{ t('merchantList.email') }}:</strong> {{ merchant.email }}</div>
          <div><strong>{{ t('merchantList.phone') }}:</strong> {{ merchant.phonenumber || '-' }}</div>
          <div><strong>{{ t('merchantList.address') }}:</strong> {{ merchant.address || '-' }}</div>
        </div>
        <div class="merchant-card-actions">
          <button @click="openEditModal(merchant)" class="btn-edit">
            {{ t('actions.edit') }}
          </button>
          <button @click="openConfirmModal('toggle', merchant)" :class="merchant.isActive ? 'btn-suspend' : 'btn-unsuspend'">
            {{ merchant.isActive ? t('actions.suspend') : t('actions.unsuspend') }}
          </button>
          <button @click="openConfirmModal('delete', merchant)" class="btn-delete">
            {{ t('actions.delete') }}
          </button>
        </div>
      </div>
      <div v-if="!filteredMerchants.length" class="mobile-empty">{{ t('merchantList.empty') }}</div>
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
    const { data } = await axios.get('https://lmgtech-e1q0.onrender.com/merchant/all', {
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
      response = await axios.put(`https://lmgtech-e1q0.onrender.com/merchant/admin/update/${form.value._id}`, formData, { headers: { Authorization: `Bearer ${token}`, 'accept-language': locale.value } })
    } else {
      response = await axios.post('https://lmgtech-e1q0.onrender.com/merchant/register', formData, { headers: { Authorization: `Bearer ${token}`, 'accept-language': locale.value } })
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
      await axios.delete(`https://lmgtech-e1q0.onrender.com/merchant/${merchantToActOn.value._id}`, { headers: { Authorization: `Bearer ${token}` } })
      merchants.value = merchants.value.filter(m => m._id !== merchantToActOn.value._id)
    } else if (modalAction.value === 'toggle') {
      const updated = { isActive: !merchantToActOn.value.isActive }
      await axios.put(`https://lmgtech-e1q0.onrender.com/merchant/admin/update/${merchantToActOn.value._id}`, updated, { headers: { Authorization: `Bearer ${token}` } })
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

const activeMerchants = computed(() => filteredMerchants.value.filter(m => m.isActive).length)

onMounted(fetchMerchants)
</script>

<style scoped>
.merchant-list {
  padding: 24px;
  background:
    radial-gradient(circle at 0% 0%, rgba(21, 101, 192, 0.1), transparent 36%),
    radial-gradient(circle at 100% 100%, rgba(33, 125, 95, 0.12), transparent 42%),
    #f6f9fc;
  min-height: 100vh;
  color: #102a43;
}
.dark .merchant-list {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  gap: 16px;
}
.header-content {
  flex: 1;
}
.title {
  font-size: clamp(1.5rem, 2.2vw, 2.1rem);
  font-weight: 800;
  margin-bottom: 2px;
  color: #102a43;
}
.dark .title {
  color: #f9fafb;
}
.subtitle {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #486581;
  margin: 0;
  font-weight: 700;
}
.dark .subtitle {
  color: #9ca3af;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.summary-chip {
  min-width: 110px;
  padding: 8px 12px;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 20px rgba(16, 42, 67, 0.07);
}

.summary-chip span {
  display: block;
  font-size: 12px;
  color: #627d98;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 8px 18px rgba(13, 71, 161, 0.28);
}
.refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(13, 71, 161, 0.34);
}

.search-container {
  margin-bottom: 16px;
}
.search-wrapper {
  position: relative;
  max-width: 460px;
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
  padding: 11px 14px 11px 44px;
  border: 1px solid #bcccdc;
  border-radius: 12px;
  background: white;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 10px rgba(16, 42, 67, 0.06);
}
.dark .search-input {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}
.search-input:focus {
  outline: none;
  border-color: #1565c0;
  box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.15);
}

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

.table-container {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 28px rgba(16, 42, 67, 0.08);
  border: 1px solid #d9e2ec;
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
  background: #f0f4f8;
}
.dark .table-header {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
}
.table-th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: #334e68;
  border-bottom: 1px solid #d9e2ec;
}
.dark .table-th {
  color: #f9fafb;
  border-bottom-color: #4b5563;
}
.table-row {
  transition: background-color 0.2s ease;
}
.table-row:hover {
  background: #f8fbff;
}
.dark .table-row:hover {
  background: rgba(59, 130, 246, 0.1);
}
.table-td {
  padding: 12px 16px;
  border-bottom: 1px solid #edf2f7;
  color: #243b53;
}
.dark .table-td {
  border-bottom-color: #4b5563;
  color: #f9fafb;
}
.status-active {
  display: inline-block;
  padding: 5px 11px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #e3f9ec;
  color: #166534;
  border: 1px solid #c4f0d6;
}
.dark .status-active {
  background: #14532d;
  color: #bbf7d0;
  border-color: #166534;
}
.status-suspended {
  display: inline-block;
  padding: 5px 11px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #fee9e9;
  color: #991b1b;
  border: 1px solid #f8b2b2;
}
.dark .status-suspended {
  background: #7f1d1d;
  color: #fca5a5;
  border-color: #991b1b;
}
.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}
.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: #1565c0;
  color: white;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.btn-edit:hover {
  transform: translateY(-1px);
}
.btn-suspend {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: #d28d02;
  color: white;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.btn-suspend:hover {
  transform: translateY(-1px);
}
.btn-unsuspend {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: #1d7a46;
  color: white;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.btn-unsuspend:hover {
  transform: translateY(-1px);
}
.btn-delete {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  background: #c12f2f;
  color: white;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.btn-delete:hover {
  transform: translateY(-1px);
}
.empty-row {
  text-align: center;
}
.empty-cell {
  padding: 48px;
  color: #627d98;
}
.dark .empty-cell {
  color: #9ca3af;
}

.add-button-container {
  text-align: right;
}
.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #102a43 0%, #243b53 100%);
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
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(16, 42, 67, 0.35);
}
.dark .add-btn:hover {
  box-shadow: 0 8px 20px rgba(249, 250, 251, 0.2);
}

.icon-sm {
  width: 16px;
  height: 16px;
}
.icon-xs {
  width: 14px;
  height: 14px;
}

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

.mobile-cards {
  display: none;
  margin-bottom: 20px;
}

.merchant-card {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 10px 20px rgba(16, 42, 67, 0.06);
}

.merchant-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
}

.card-title {
  font-weight: 700;
}

.card-subtitle {
  color: #627d98;
  font-size: 13px;
}

.merchant-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  margin-bottom: 10px;
}

.merchant-card-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.merchant-card-actions .btn-delete {
  grid-column: 1 / -1;
}

.mobile-empty {
  text-align: center;
  color: #627d98;
  padding: 18px;
}

.form-input {
  width: 100%;
  border: 1px solid #d1d9e0;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
}

.form-input:focus {
  outline: none;
  border-color: #1565c0;
  box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.15);
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-toggle-btn {
  position: absolute;
  right: 10px;
  border: none;
  background: transparent;
  color: #486581;
  font-size: 12px;
  cursor: pointer;
}

.btn-submit {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  background: #1565c0;
  color: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loader-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@media (max-width: 768px) {
  .merchant-list {
    padding: 16px;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .summary-chip {
    flex: 1 1 120px;
  }

  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: block;
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

  .add-button-container {
    text-align: left;
  }
}

@media (max-width: 460px) {
  .merchant-card-actions {
    grid-template-columns: 1fr;
  }

  .merchant-card-actions .btn-delete {
    grid-column: auto;
  }
}
</style>

