<template>
  <div class="p-6 bg-slate-50 dark:bg-slate-950 min-h-screen">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <p class="text-sm uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400 mb-1">{{ t('merchantList.subtitle') }}</p>
        <h2 class="text-3xl font-semibold text-slate-900 dark:text-slate-100">
          {{ t('merchantList.title') }}
        </h2>
      </div>
      <button
        @click="fetchMerchants"
        class="inline-flex items-center justify-center rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition duration-200 hover:bg-sky-700"
      >
        {{ t('actions.refresh') }}
      </button>
    </div>

    <!-- Search Bar -->
    <div class="mb-4">
      <input
        v-model="searchQuery"
        :placeholder="t('merchantList.searchPlaceholder')"
        class="w-full md:w-1/3 border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-gray-100"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-6 text-gray-500 dark:text-gray-400">
      <div class="loader mb-2 mx-auto"></div>
      {{ t('merchantList.loading') }}
    </div>

    <!-- Merchant Table -->
    <div v-else class="overflow-x-auto rounded-xl border border-slate-200 bg-white/80 shadow-sm dark:border-slate-800 dark:bg-slate-900/90">
      <table class="min-w-full text-sm text-left">
        <thead class="bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-slate-300">
          <tr>
            <th class="px-5 py-4 font-medium">#</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.name') }}</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.email') }}</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.phone') }}</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.businessName') }}</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.address') }}</th>
            <th class="px-5 py-4 font-medium">{{ t('merchantList.status') }}</th>
            <th class="px-5 py-4 font-medium text-center">{{ t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(merchant, index) in filteredMerchants"
            :key="merchant._id"
            class="border-t border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            <td class="px-4 py-2">{{ index + 1 }}</td>
            <td class="px-4 py-2">{{ merchant.fullName }}</td>
            <td class="px-4 py-2">{{ merchant.email }}</td>
            <td class="px-4 py-2">{{ merchant.phonenumber || '-' }}</td>
            <td class="px-4 py-2">{{ merchant.businessName }}</td>
            <td class="px-4 py-2">{{ merchant.address }}</td>
            <td class="px-4 py-2">
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-semibold border',
                  merchant.isActive
                    ? 'bg-green-100 text-green-700 border-green-400 dark:bg-green-700 dark:text-green-100 dark:border-green-600'
                    : 'bg-red-100 text-red-700 border-red-400 dark:bg-red-700 dark:text-red-100 dark:border-red-600'
                ]"
              >
                {{ merchant.isActive ? t('merchantList.active') : t('merchantList.suspended') }}
              </span>
            </td>
            <td class="px-4 py-2 text-center flex flex-wrap justify-center gap-1">
              <button
                @click="openEditModal(merchant)"
                class="px-3 py-1 rounded bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-semibold hover:scale-105 transition"
              >
                {{ t('actions.edit') }}
              </button>
              <button
                @click="openConfirmModal('toggle', merchant)"
                :class="[
                  'px-3 py-1 rounded text-white text-xs font-semibold hover:scale-105 transition',
                  merchant.isActive ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'
                ]"
              >
                {{ merchant.isActive ? t('actions.suspend') : t('actions.unsuspend') }}
              </button>
              <button
                @click="openConfirmModal('delete', merchant)"
                class="px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-xs font-semibold hover:scale-105 transition"
              >
                {{ t('actions.delete') }}
              </button>
            </td>
          </tr>

          <tr v-if="!filteredMerchants.length">
            <td colspan="8" class="text-center py-6 text-gray-500 dark:text-gray-400">
              {{ t('merchantList.empty') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Merchant Button -->
    <div class="mt-6 text-right">
      <button @click="openAddModal" class="inline-flex items-center justify-center rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-lg transition duration-200 hover:bg-slate-800">
        + {{ t('merchant.add') }}
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
  try {
    const token = localStorage.getItem('adminToken')
    const { data } = await axios.get('https://lmgtech-4.onrender.com/merchant/all', {
      headers: { Authorization: `Bearer ${token}` },
    })
    merchants.value = data || []
  } catch (err) {
    console.error(err)
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
  if (!searchQuery.value.trim()) return merchants.value
  const q = searchQuery.value.toLowerCase()
  return merchants.value.filter(
    m => m.fullName?.toLowerCase().includes(q) ||
         m.email?.toLowerCase().includes(q) ||
         m.businessName?.toLowerCase().includes(q)
  )
})

onMounted(fetchMerchants)
</script>

<style scoped>
/* Loader */
.loader, .loader-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  display: inline-block;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Form Inputs */
.form-input {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #ffffff;
  color: #0f172a;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.dark .form-input {
  background-color: #0f172a;
  color: #e2e8f0;
  border-color: #334155;
}
.form-input:focus {
  outline: none;
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.18);
}

/* Add Merchant Button */
.mt-6.text-right > button {
  background-color: #0f172a;
  color: white;
  padding: 0.75rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 700;
  border-radius: 0.75rem;
  box-shadow: 0 12px 25px rgba(15, 23, 42, 0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}
.mt-6.text-right > button:hover {
  transform: translateY(-1px);
  background-color: #111827;
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.18);
}

/* Merchant Table */
table {
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
}
thead {
  background-color: #f8fafc;
}
thead th {
  padding: 1rem 1.25rem;
  font-weight: 700;
  text-align: left;
  color: #111827;
}
.dark thead {
  background-color: #111827;
}
.dark thead th {
  color: #e2e8f0;
}
tbody td {
  padding: 0.85rem 1.25rem;
  color: #334155;
  border-bottom: 1px solid #e2e8f0;
}
.dark tbody td {
  color: #cbd5e1;
  border-bottom-color: #334155;
}

/* Status Badges */
td span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
td span.bg-green-100 {
  background-color: rgba(22, 163, 74, 0.14);
  color: #064e3b;
  border: 1px solid rgba(16, 185, 129, 0.35);
}
td span.bg-red-100 {
  background-color: rgba(239, 68, 68, 0.14);
  color: #7f1d1d;
  border: 1px solid rgba(239, 68, 68, 0.35);
}

td > button {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
}
td > button:hover {
  transform: scale(1.05);
}

/* Modals */
.fixed.inset-0.flex.items-center.justify-center {
  position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px); overflow: hidden;
}
.bg-white.dark\:bg-slate-900 {
  width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; overflow-x: hidden;
  border-radius: 0.75rem; padding: 1.5rem; position: relative;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15); transition: all 0.3s ease-in-out;
}

/* Password Field */
.password-wrapper { display: flex; align-items: center; position: relative; width: 100%; }
.password-wrapper .form-input { flex: 1; padding-right: 3rem; }
.password-toggle-btn {
  position: absolute; right: 0.75rem; background: none; border: none; cursor: pointer;
  font-size: 0.85rem; color: #6b7280; height: 100%; display: flex; align-items: center; transition: color 0.2s;
}
.password-toggle-btn:hover { color: #2563eb; }

/* Submit Button */
.btn-submit { background-color: #3b82f6; color: white; font-weight: 600; padding: 0.6rem 1.2rem; border-radius: 0.5rem; font-size: 1rem; width: 100%; transition: all 0.2s ease-in-out; }
.btn-submit:hover { background-color: #2563eb; transform: translateY(-1px) scale(1.02); }

/* Responsive Table Cards */
@media (max-width: 768px) {
  table thead { display: none; }
  table tbody tr { display: block; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 1rem; padding: 0.5rem; background-color: white; }
  table tbody td { display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e5e7eb; }
  table tbody td:last-child { border-bottom: 0; flex-wrap: wrap; gap: 0.25rem; justify-content: center; }
  td > button { flex: 1 1 45%; margin-bottom: 0.25rem; }
}

/* Fullscreen Modals on Mobile */
@media (max-width: 640px) {
  .bg-white.dark\:bg-slate-900 { width: 95% !important; max-height: 90vh !important; border-radius: 0.5rem !important; padding: 1rem !important; overflow-y: auto; overflow-x: hidden; }
  .grid.grid-cols-1.md\:grid-cols-2.gap-4 { grid-template-columns: 1fr !important; }
  input, button { max-width: 100%; }
  .mt-6.text-center > button { width: 100%; font-size: 1rem; padding: 0.75rem; }
}
</style>
