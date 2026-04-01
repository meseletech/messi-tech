<template>
  <div :class="['wrapper', theme]">
    <!-- Navbar -->
    <Navbar 
      :theme="theme"
      @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
      @update-theme="theme = $event"
    />

    <div class="layout">
      <!-- Sidebar -->
      <Sidebar :isOpen="isSidebarOpen" />

      <!-- Overlay for mobile -->
      <div 
        v-if="isMobile && isSidebarOpen" 
        class="overlay" 
        @click="isSidebarOpen = false">
      </div>

      <!-- Main content -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';

const isSidebarOpen = ref(true);
const theme = ref(localStorage.getItem("theme") || "light");
const isMobile = ref(window.innerWidth <= 768);

function handleResize() {
  isMobile.value = window.innerWidth <= 768;

  // auto open sidebar on desktop
  if (!isMobile.value) isSidebarOpen.value = true;
}

onMounted(() => {
  window.addEventListener('resize', handleResize);
  handleResize();
});

watch(theme, (newTheme) => {
  localStorage.setItem("theme", newTheme);
});
</script>

<style scoped>
/* Navbar spacing */
.wrapper {
  padding-top: 64px;
}

/* Layout */
.layout {
  display: flex;
  align-items: flex-start;
}

/* Main content area */
.content {
  flex: 1;
  padding: 20px;
  margin-left: 0;
  height: calc(100vh - 64px);
  overflow-y: auto;
  transition: margin-left 0.3s ease;
}

/* Remove left margin when collapsed (desktop only) */
@media (min-width: 769px) {
  .content.collapsed {
    margin-left: 0;
  }
}

/* Mobile: content always full width */
@media (max-width: 768px) {
  .content {
    margin-left: 0;
  }
}

/* Mobile dim overlay */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.45);
  z-index: 40;
}

/* Needed for fixed navbar */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
}
</style>
