<template>
  <header class="navbar">
    <!-- Sidebar toggle -->
    <button class="hamburger-btn" @click="$emit('toggle-sidebar')">☰</button>

    <!-- Logo -->
    <h1 class="logo">{{ $t('dashboard.title') }}</h1>

    <!-- Controls -->
    <div class="controls" ref="dropdownRef">
      <button class="dropdown-btn" @click.stop="dropdownOpen = !dropdownOpen">⋮</button>

      <div v-if="dropdownOpen" class="dropdown-menu">
        <div class="dropdown-item">
          <label>Language:</label>
          <select v-model="locale" @change="onLocaleChange">
            <option value="en">EN</option>
            <option value="am">AM</option>
            <option value="om">OM</option>
          </select>
        </div>
        <div class="dropdown-item">
          <ThemeSwitcher :theme="theme" @update-theme="onThemeChange" />
        </div>
        <button class="logout-btn" @click="handleLogout">{{ $t('actions.logout') }}</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import ThemeSwitcher from './ThemeSwitcher.vue';

const emit = defineEmits(['toggle-sidebar', 'update-theme']);
const router = useRouter();
const { locale } = useI18n();
const theme = ref(localStorage.getItem('theme') || 'light');
const dropdownOpen = ref(false);
const dropdownRef = ref(null);

onMounted(() => document.addEventListener('click', handleClickOutside));
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside));

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false;
  }
}

function handleLogout() {
  localStorage.removeItem('adminToken'); // or merchantToken if using merchant
  router.replace('/login');
}

function onLocaleChange() {
  localStorage.setItem('locale', locale.value);
}

function onThemeChange(newTheme) {
  theme.value = newTheme;
  emit('update-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}
</script><style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: white;;
  color: rgb(26, 2, 2);
  padding: 0.16rem 0.5rem;
  padding-right: 2rem; /* NEW: prevent button from touching screen edge */
  font-family: 'Segoe UI', sans-serif;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  position: sticky;
  top: 0;
  z-index: 50;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  border-radius: 0 0 10px 10px;
}

.hamburger-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  color: rgb(27, 23, 23);
  cursor: pointer;
}

.logo {
  flex: 1;
  text-align: center;
  font-weight: 700;
  font-size: 1.6rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.controls {
  position: relative;
  margin-right: 1rem; /* NEW: pushes button left */
}

.dropdown-btn {
  background: #e8e9eb;
  color: rgb(27, 24, 24);
  padding: 0.35rem 0.7rem;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.dropdown-btn:hover {
  background: #1d4ed8;
}

/* ----------- UPDATED DROPDOWN POSITION (15% LEFT) ----------- */
:deep(.dropdown-menu) {
  position: absolute;
  right: -15%; /* Shift left by responsive 15% */
  top: 120%;
  background: white;
  color: #1f2937;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 220px;
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
/* ----------------------------------------------------------- */

.dropdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-item label {
  font-weight: 500;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.dropdown-item select {
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  font-size: 0.85rem;
}

.logout-btn {
  width: 100%;
  background-color: #b91010;
  border: none;
  color: white;
  padding: 0.45rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}
.logout-btn:hover {
  background-color: #059669;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .logo {
    font-size: 1.2rem;
    text-align: left;
  }

  .controls {
    margin-right: 0.5rem; /* NEW: smaller spacing on mobile */
  }

  :deep(.dropdown-menu) {
    min-width: 180px;
    padding: 0.5rem;
    right: -25%; /* More left on mobile for better fit */
  }

  .dropdown-item select {
    font-size: 0.8rem;
  }

  .logout-btn {
    font-size: 0.85rem;
    padding: 0.35rem;
  }
}
</style>
