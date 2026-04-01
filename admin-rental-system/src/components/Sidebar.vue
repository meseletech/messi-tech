<template>
  <aside :class="['sidebar', { 'sidebar-closed': !isOpen, mobile: isMobile, 'sidebar-open': isOpen }]">
    
    <div class="sidebar-header">
      <div>
        <p class="brand-label">Admin Panel</p>
        <h2>{{ $t('dashboard.title') }}</h2>
      </div>
      <button v-if="isMobile" class="close-btn" @click="$emit('toggle-sidebar')">✕</button>
    </div>

    <!-- Scrollable menu -->
    <nav class="menu">
      <button type="button" class="menu-item" @click="navigate('/dashboard')" :class="{ 'active-link': route.path === '/dashboard' }">
        <span class="icon">🏠</span>
        <span>{{ $t('dashboard.title') }}</span>
      </button>

      <button type="button" class="menu-item" @click="navigate('/merchant-list')" :class="{ 'active-link': route.path === '/merchant-list' }">
        <span class="icon">📦</span>
        <span>{{ $t('merchantList.title') }}</span>
      </button>

      <button type="button" class="menu-item" @click="navigate('/customer-list')" :class="{ 'active-link': route.path === '/customer-list' }">
        <span class="icon">👥</span>
        <span>{{ $t('customer.listTitle') }}</span>
      </button>

      <button type="button" class="menu-item" @click="navigate('/booking-list')" :class="{ 'active-link': route.path === '/booking-list' }">
        <span class="icon">📅</span>
        <span>{{ $t('bookingList.title') }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const props = defineProps({
  isOpen: { type: Boolean, default: true }
});

const router = useRouter();
const route = useRoute();
const isMobile = ref(window.innerWidth <= 768);

function handleResize() {
  isMobile.value = window.innerWidth <= 768;
}

function navigate(path) {
  router.push(path).catch(() => {})
}

onMounted(() => window.addEventListener('resize', handleResize));
onUnmounted(() => window.removeEventListener('resize', handleResize));
</script>

<style scoped>
/* FIXED SIDEBAR */
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  padding: 1.25rem;
  box-shadow: 2px 0 18px rgba(15, 23, 42, 0.08);
  border-right: 1px solid rgba(148, 163, 184, 0.16);
  position: fixed;
  top: 64px; /* Below navbar */
  left: 0;
  height: calc(100vh - 64px);
  overflow: hidden;
  transition: transform 0.3s ease;
  z-index: 60;
  color: #0f172a;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.brand-label {
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #475569;
  margin-bottom: 0.25rem;
}

.sidebar-header h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.close-btn {
  background: rgba(15, 23, 42, 0.05);
  border: none;
  color: #0f172a;
  width: 34px;
  height: 34px;
  border-radius: 9999px;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: rgba(15, 23, 42, 0.12);
}

/* Sidebar content scrolls here */
.menu {
  margin-top: 1rem;
  overflow-y: auto;
  height: calc(100% - 74px);
  padding-right: 4px;
}

.sidebar-closed {
  transform: translateX(-100%);
}

.mobile {
  width: 72%;
  max-width: 280px;
  border-radius: 0;
  top: 0;
  height: 100vh;
  padding-top: 74px;
  transform: translateX(-100%);
}

.mobile.sidebar-open { transform: translateX(0); }
.mobile.sidebar-closed { transform: translateX(-100%); }

/* Menu Styling */
.menu-item {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  width: 100%;
  padding: 0.95rem 1rem;
  border-radius: 14px;
  color: #334155;
  background: rgba(15, 23, 42, 0.015);
  border: 1px solid transparent;
  margin-bottom: 0.6rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background: rgba(56, 189, 248, 0.12);
  color: #0f172a;
  transform: translateX(1px);
}

.menu-item.active-link {
  background: #0284c7;
  color: #ffffff;
  border-color: rgba(2, 132, 199, 0.4);
}

.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 12px;
  background: rgba(2, 132, 199, 0.12);
  color: #0369a1;
  font-size: 1rem;
}

.menu-item.active-link .icon {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.menu-item span:last-child {
  font-size: 0.96rem;
  font-weight: 600;
}
</style>
