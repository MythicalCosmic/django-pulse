import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)

  // Initialize from localStorage
  const stored = localStorage.getItem('telescope-theme')
  if (stored) {
    isDark.value = stored === 'dark'
  }

  function toggle() {
    isDark.value = !isDark.value
  }

  watch(isDark, (dark) => {
    localStorage.setItem('telescope-theme', dark ? 'dark' : 'light')
    document.documentElement.classList.toggle('light', !dark)
  }, { immediate: true })

  return { isDark, toggle }
})
