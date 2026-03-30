import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'
import type { TelescopeEntry, StatusResponse } from '../types'

export const useEntriesStore = defineStore('entries', () => {
  const entries = ref<TelescopeEntry[]>([])
  const loading = ref(false)
  const hasMore = ref(false)
  const status = ref<StatusResponse | null>(null)

  async function fetchEntries(params?: Record<string, string>) {
    loading.value = true
    try {
      const data = await api.entries(params)
      entries.value = data.entries
      hasMore.value = data.has_more
    } finally {
      loading.value = false
    }
  }

  async function fetchByType(typeSlug: string, params?: Record<string, string>) {
    loading.value = true
    try {
      const data = await api.entriesByType(typeSlug, params)
      entries.value = data.entries
      hasMore.value = data.has_more
    } finally {
      loading.value = false
    }
  }

  async function loadMore(typeSlug?: string) {
    if (!entries.value.length || !hasMore.value) return
    const lastId = entries.value[entries.value.length - 1].uuid
    loading.value = true
    try {
      const params: Record<string, string> = { before: lastId }
      const data = typeSlug
        ? await api.entriesByType(typeSlug, params)
        : await api.entries(params)
      entries.value.push(...data.entries)
      hasMore.value = data.has_more
    } finally {
      loading.value = false
    }
  }

  async function fetchStatus() {
    status.value = await api.status()
  }

  function prependEntry(entry: TelescopeEntry) {
    entries.value.unshift(entry)
    // Keep list manageable
    if (entries.value.length > 200) {
      entries.value = entries.value.slice(0, 200)
    }
  }

  function clear() {
    entries.value = []
    hasMore.value = false
  }

  return { entries, loading, hasMore, status, fetchEntries, fetchByType, loadMore, fetchStatus, prependEntry, clear }
})
