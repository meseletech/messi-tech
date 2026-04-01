<template>
  <aside :class="['sidebar', { 'sidebar-closed': !isOpen, mobile: isMobile, 'sidebar-open': isOpen }]">
    
    <div class="sidebar-header">
      <h2>{{ $t('dashboard.title') }}</h2>
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
  width: 220px;
  background: white;
  padding: 1rem;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
  position: fixed;
  top: 64px; /* Below navbar */
  left: 0;
  height: calc(100vh - 64px);
  overflow: hidden; /* Prevent scrolling */
  transition: transform 0.3s ease;
  z-index: 60;
}

/* Sidebar content scrolls here */
.menu {
  margin-top: 1rem;
  overflow-y: auto;
  height: calc(100% - 60px);
  padding-right: 4px;
}

/* DESKTOP CLOSED */
.sidebar-closed {
  transform: translateX(-100%);
}

/* MOBILE MODE */
.mobile {
  width: 70%;
  max-width: 260px;
  border-radius: 0;
  top: 0;
  height: 100vh;
  padding-top: 70px;
  transform: translateX(-100%);
}

.mobile.sidebar-open { transform: translateX(0); }
.mobile.sidebar-closed { transform: translateX(-100%); }

/* Menu Styling */
.menu-item {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  color: #6b7280;
  text-decoration: none;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: 0.2s;
}

.menu-item:hover,
.menu-item.router-link-active,
.menu-item.active-link {
  background: #7184b7;
  color: white;
}
</style>
