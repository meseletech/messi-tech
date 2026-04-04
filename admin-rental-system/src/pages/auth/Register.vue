<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ $t('register') }}</h2>

      <form @submit.prevent="submitRegister">
        <input v-model="fullName" type="text" :placeholder="$t('name')" required />
        <input v-model="email" type="email" :placeholder="$t('email')" required />

        <div class="password-container">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            :placeholder="$t('password')"
            required
          />
          <button type="button" class="toggle-password" @click="togglePassword">
            {{ showPassword ? '🙈' : '👁' }}
          </button>
        </div>

        <input v-model="phonenumber" type="text" :placeholder="$t('phone')" required />
        <input v-model="address" type="text" :placeholder="$t('address')" required />

        <button type="submit" :disabled="loading" class="submit-btn">
          <span v-if="loading" class="progress-bar"></span>
          {{ loading ? $t('loading') : $t('register') }}
        </button>

        <p class="switch-link" @click="goToLogin">
          {{ $t('already_have_account') }} <strong>{{ $t('log_in') }}</strong>
        </p>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../utils/Api'

export default {
  setup() {
    const fullName = ref('')
    const email = ref('')
    const password = ref('')
    const phonenumber = ref('')
    const address = ref('')
    const error = ref('')
    const loading = ref(false)
    const showPassword = ref(false)
    const router = useRouter()

    const togglePassword = () => (showPassword.value = !showPassword.value)

    const submitRegister = async () => {
      try {
        loading.value = true
        error.value = ''
        const lang = localStorage.getItem('locale') || 'en'

        await api.post(
          '/register',
          { fullName: fullName.value, email: email.value, password: password.value, phonenumber: Number(phonenumber.value), address: address.value },
          { headers: { 'Accept-Language': lang } }
        )

        setTimeout(() => router.push('/dashboard'), 1500)
      } catch (err) {
        console.error('❌ Registration failed:', err)
        error.value = err.response?.data?.message || 'Registration failed'
      } finally {
        loading.value = false
      }
    }

    const goToLogin = () => router.push('/login')

    return { fullName, email, password, phonenumber, address, error, loading, showPassword, togglePassword, submitRegister, goToLogin }
  },
}
</script>
<style scoped>
/* ==============================
   GLOBAL CONTAINER
================================= */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 15px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
}

/* ==============================
   CARD
================================= */
.auth-card {
  background: #fff;
  padding: 25px 20px;
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

/* Title */
.auth-card h2 {
  margin-bottom: 20px;
  font-size: 22px;
  font-weight: 700;
  color: #1e3a8a;
}

/* ==============================
   INPUT FIELDS
================================= */
.auth-card input {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 16px;
  box-sizing: border-box;
  transition: 0.2s;
}

.auth-card input:focus {
  border-color: #007bff;
  box-shadow: 0 0 6px rgba(0,123,255,0.3);
  background: #fff;
}

/* ==============================
   PASSWORD FIELD WITH TOGGLE
================================= */
.password-container {
  position: relative;
  display: flex;
  align-items: center;
  margin: 8px 0;
}

.password-container input {
  flex: 1;
  padding-right: 42px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #555;
  padding: 5px;
  transition: 0.2s;
}

.toggle-password:hover {
  opacity: 0.8;
}

/* ==============================
   SUBMIT BUTTON
================================= */
.submit-btn {
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  border: none;
  border-radius: 8px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: 0.2s ease-in-out;
}

.submit-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* PROGRESS BAR */
.progress-bar {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0%;
  background: rgba(255, 255, 255, 0.3);
  animation: progress 1.5s linear forwards;
}

@keyframes progress {
  from { width: 0%; }
  to { width: 100%; }
}

/* ==============================
   SWITCH LINK & ERRORS
================================= */
.switch-link {
  margin-top: 15px;
  font-size: 14px;
  color: #007bff;
  cursor: pointer;
}

.switch-link strong {
  font-weight: bold;
}

.switch-link:hover {
  text-decoration: underline;
}

.error {
  color: red;
  margin-top: 10px;
  font-size: 14px;
  font-weight: bold;
  text-align: center;
}

/* ==============================
   SPINNER (if needed)
================================= */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ==============================
   RESPONSIVE DESIGN
================================= */
@media (max-width: 480px) {
  .auth-card {
    padding: 20px 15px;
    max-width: 90%;
  }

  .auth-card h2 {
    font-size: 20px;
  }

  .auth-card input,
  .submit-btn {
    font-size: 14px;
    padding: 10px;
  }

  .toggle-password {
    font-size: 16px;
  }

  .switch-link {
    font-size: 12px;
  }

  .error {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .auth-card {
    padding: 26px 20px;
  }

  .auth-card h2 {
    font-size: 22px;
  }
}
</style>
