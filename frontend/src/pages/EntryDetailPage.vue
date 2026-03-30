<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import type { TelescopeEntry } from '../types'
import KeyValueTable from '../components/KeyValueTable.vue'
import CodeBlock from '../components/CodeBlock.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { formatDateTime } from '../composables/useTimeAgo'

const route = useRoute()
const router = useRouter()
const entry = ref<TelescopeEntry | null>(null)
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const data = await api.entryDetail(route.params.uuid as string)
    entry.value = data.entry
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <button @click="router.back()" class="text-sm text-surface-400 hover:text-surface-200 mb-4 transition-colors">
      ← Back
    </button>

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-8 w-64"></div>
      <div class="skeleton h-48 w-full rounded-xl"></div>
    </div>

    <div v-else-if="entry" class="space-y-6 animate-fade-in">
      <div class="flex items-center gap-3">
        <StatusBadge :type="entry.type_slug" />
        <h1 class="text-xl font-bold text-surface-100 light:text-surface-900">{{ entry.type_label }} Detail</h1>
        <span class="text-xs text-surface-500">{{ formatDateTime(entry.created_at) }}</span>
      </div>

      <!-- Tags -->
      <div v-if="entry.tags?.length" class="flex gap-2 flex-wrap">
        <span
          v-for="tag in entry.tags"
          :key="tag"
          class="inline-block px-2 py-1 text-xs rounded-md bg-surface-800 light:bg-surface-100 text-surface-400 light:text-surface-500 border border-surface-700 light:border-surface-200"
        >
          {{ tag }}
        </span>
      </div>

      <!-- Content as key-value table -->
      <KeyValueTable title="Content" :data="entry.content" />

      <!-- Raw JSON -->
      <details class="group">
        <summary class="text-xs text-surface-500 cursor-pointer hover:text-surface-300 transition-colors">
          Raw JSON
        </summary>
        <div class="mt-2">
          <CodeBlock :code="JSON.stringify(entry.content, null, 2)" language="json" />
        </div>
      </details>
    </div>
  </div>
</template>
