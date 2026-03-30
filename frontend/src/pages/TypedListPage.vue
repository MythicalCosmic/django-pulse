<script setup lang="ts">
import { onMounted, ref, watch, onUnmounted } from 'vue'
import { api } from '../api'
import { getWebSocket } from '../websocket'
import type { TelescopeEntry } from '../types'
import EntryTable from '../components/EntryTable.vue'
import SearchBar from '../components/SearchBar.vue'

const props = defineProps<{ typeSlug: string; title: string }>()

const entries = ref<TelescopeEntry[]>([])
const loading = ref(true)
const hasMore = ref(false)
const search = ref('')

const ws = getWebSocket()
const unsub = ws.onEntry((entry) => {
  if (entry.type_slug === props.typeSlug) {
    entries.value.unshift(entry)
    if (entries.value.length > 200) entries.value = entries.value.slice(0, 200)
  }
})

async function load(searchQuery?: string) {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (searchQuery) params.search = searchQuery
    const data = await api.entriesByType(props.typeSlug, params)
    entries.value = data.entries
    hasMore.value = data.has_more
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (!entries.value.length || !hasMore.value) return
  const last = entries.value[entries.value.length - 1]
  const data = await api.entriesByType(props.typeSlug, { before: last.uuid })
  entries.value.push(...data.entries)
  hasMore.value = data.has_more
}

watch(() => props.typeSlug, () => load())
onMounted(() => load())
onUnmounted(unsub)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-surface-100 light:text-surface-900">{{ title }}</h1>
      <SearchBar v-model="search" :placeholder="`Search ${title.toLowerCase()}...`" @search="load" class="w-72" />
    </div>

    <div class="rounded-xl border border-surface-800 light:border-surface-200 overflow-hidden">
      <EntryTable :entries="entries" :loading="loading" :detail-route="`${typeSlug}-detail`" />

      <div v-if="hasMore" class="p-4 text-center border-t border-surface-800 light:border-surface-200">
        <button @click="loadMore" class="text-sm text-primary-400 hover:text-primary-300 transition-colors">
          Load more...
        </button>
      </div>
    </div>
  </div>
</template>
