<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue'
import { api } from '../api'
import { getWebSocket } from '../websocket'
import type { TelescopeEntry } from '../types'
import SearchBar from '../components/SearchBar.vue'
import { formatTimeAgo } from '../composables/useTimeAgo'

const entries = ref<TelescopeEntry[]>([])
const loading = ref(true)
const hasMore = ref(false)
const search = ref('')

const ws = getWebSocket()
const unsub = ws.onEntry((entry) => {
  if (entry.type_slug === 'exception') {
    entries.value.unshift(entry)
    if (entries.value.length > 200) entries.value = entries.value.slice(0, 200)
  }
})

async function load(searchQuery?: string) {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (searchQuery) params.search = searchQuery
    const data = await api.entriesByType('exception', params)
    entries.value = data.entries
    hasMore.value = data.has_more
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
onUnmounted(unsub)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-surface-100 light:text-surface-900">Exceptions</h1>
      <SearchBar v-model="search" placeholder="Search exceptions..." @search="load" class="w-72" />
    </div>

    <div class="rounded-xl border border-surface-800 light:border-surface-200 overflow-hidden">
      <div class="divide-y divide-surface-800/50 light:divide-surface-100">
        <div v-if="loading && entries.length === 0" v-for="i in 5" :key="i" class="p-4">
          <div class="skeleton h-5 w-48 mb-2"></div>
          <div class="skeleton h-3 w-96"></div>
        </div>

        <div
          v-for="entry in entries"
          :key="entry.uuid"
          class="p-4 hover:bg-surface-800/50 light:hover:bg-surface-50 transition-colors cursor-pointer animate-fade-in"
          @click="$router.push({ name: 'exception-detail', params: { uuid: entry.uuid } })"
        >
          <div class="flex items-center gap-3 mb-1">
            <span class="text-red-400 font-semibold text-sm">{{ entry.content?.class }}</span>
            <span class="text-xs text-surface-500">{{ formatTimeAgo(entry.created_at) }}</span>
          </div>
          <p class="text-xs text-surface-400 font-mono truncate">{{ entry.content?.message }}</p>
          <p v-if="entry.content?.file" class="text-xs text-surface-600 mt-1 font-mono">
            {{ entry.content.file }}:{{ entry.content.line }}
          </p>
        </div>
      </div>

      <div v-if="!loading && entries.length === 0" class="text-center py-16 text-surface-500">
        <div class="text-4xl mb-3 opacity-30">⚠</div>
        <p>No exceptions recorded</p>
      </div>

      <div v-if="hasMore" class="p-4 text-center border-t border-surface-800 light:border-surface-200">
        <button @click="load()" class="text-sm text-primary-400 hover:text-primary-300 transition-colors">
          Load more...
        </button>
      </div>
    </div>
  </div>
</template>
