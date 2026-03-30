<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue'
import { api } from '../api'
import { getWebSocket } from '../websocket'
import type { TelescopeEntry } from '../types'
import SearchBar from '../components/SearchBar.vue'
import DurationBadge from '../components/DurationBadge.vue'
import { formatTimeAgo } from '../composables/useTimeAgo'

const entries = ref<TelescopeEntry[]>([])
const loading = ref(true)
const hasMore = ref(false)
const search = ref('')

const ws = getWebSocket()
const unsub = ws.onEntry((entry) => {
  if (entry.type_slug === 'query') {
    entries.value.unshift(entry)
    if (entries.value.length > 200) entries.value = entries.value.slice(0, 200)
  }
})

async function load(searchQuery?: string) {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (searchQuery) params.search = searchQuery
    const data = await api.entriesByType('query', params)
    entries.value = data.entries
    hasMore.value = data.has_more
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!entries.value.length || !hasMore.value) return
  const last = entries.value[entries.value.length - 1]
  const data = await api.entriesByType('query', { before: last.uuid })
  entries.value.push(...data.entries)
  hasMore.value = data.has_more
}

onMounted(() => load())
onUnmounted(unsub)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-surface-100 light:text-surface-900">Queries</h1>
      <SearchBar v-model="search" placeholder="Search SQL..." @search="load" class="w-72" />
    </div>

    <div class="rounded-xl border border-surface-800 light:border-surface-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-surface-800 light:border-surface-200 bg-surface-800/30 light:bg-surface-50">
            <th class="text-left py-3 px-4 text-xs uppercase tracking-wider text-surface-500 font-medium">SQL</th>
            <th class="text-left py-3 px-4 text-xs uppercase tracking-wider text-surface-500 font-medium">Flags</th>
            <th class="text-right py-3 px-4 text-xs uppercase tracking-wider text-surface-500 font-medium">Duration</th>
            <th class="text-right py-3 px-4 text-xs uppercase tracking-wider text-surface-500 font-medium">Time</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && entries.length === 0" v-for="i in 8" :key="i">
            <td class="py-3 px-4"><div class="skeleton h-4 w-96"></div></td>
            <td class="py-3 px-4"><div class="skeleton h-4 w-16"></div></td>
            <td class="py-3 px-4"><div class="skeleton h-4 w-16 ml-auto"></div></td>
            <td class="py-3 px-4"><div class="skeleton h-4 w-12 ml-auto"></div></td>
          </tr>
          <tr
            v-for="entry in entries"
            :key="entry.uuid"
            class="border-b border-surface-800/50 light:border-surface-100 hover:bg-surface-800/50 light:hover:bg-surface-50 transition-colors cursor-pointer animate-fade-in"
            @click="$router.push({ name: 'query-detail', params: { uuid: entry.uuid } })"
          >
            <td class="py-3 px-4 font-mono text-xs text-surface-300 light:text-surface-700 truncate max-w-lg">
              {{ entry.content?.sql }}
            </td>
            <td class="py-3 px-4">
              <div class="flex gap-1">
                <span v-if="entry.content?.slow" class="px-1.5 py-0.5 text-xs rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">slow</span>
                <span v-if="entry.content?.n_plus_one" class="px-1.5 py-0.5 text-xs rounded bg-red-500/20 text-red-400 border border-red-500/30">N+1</span>
              </div>
            </td>
            <td class="py-3 px-4 text-right">
              <DurationBadge v-if="entry.content?.duration" :ms="entry.content.duration" />
            </td>
            <td class="py-3 px-4 text-right text-xs text-surface-500 whitespace-nowrap">
              {{ formatTimeAgo(entry.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && entries.length === 0" class="text-center py-16 text-surface-500">
        <div class="text-4xl mb-3 opacity-30">⛁</div>
        <p>No queries recorded</p>
      </div>

      <div v-if="hasMore" class="p-4 text-center border-t border-surface-800 light:border-surface-200">
        <button @click="loadMore" class="text-sm text-primary-400 hover:text-primary-300 transition-colors">
          Load more...
        </button>
      </div>
    </div>
  </div>
</template>
