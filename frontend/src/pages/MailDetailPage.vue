<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import type { TelescopeEntry } from '../types'
import KeyValueTable from '../components/KeyValueTable.vue'

const route = useRoute()
const router = useRouter()
const entry = ref<TelescopeEntry | null>(null)
const loading = ref(true)
const showHtml = ref(false)

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
      ← Back to Mail
    </button>

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-8 w-64"></div>
      <div class="skeleton h-48 w-full rounded-xl"></div>
    </div>

    <div v-else-if="entry" class="space-y-6 animate-fade-in">
      <h1 class="text-xl font-bold text-surface-100 light:text-surface-900">{{ entry.content?.subject }}</h1>

      <KeyValueTable
        title="Email Details"
        :data="{
          'From': entry.content?.from,
          'To': entry.content?.to?.join(', '),
          'CC': entry.content?.cc?.join(', ') || '—',
          'BCC': entry.content?.bcc?.join(', ') || '—',
          'Subject': entry.content?.subject,
          'Attachments': entry.content?.attachments?.join(', ') || 'None',
        }"
      />

      <div v-if="entry.content?.html_body" class="rounded-xl border border-surface-800 light:border-surface-200 overflow-hidden">
        <div class="px-4 py-2.5 bg-surface-800/50 light:bg-surface-50 border-b border-surface-800 light:border-surface-200 flex items-center justify-between">
          <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-400">Email Body</h3>
          <button @click="showHtml = !showHtml" class="text-xs text-primary-400 hover:text-primary-300">
            {{ showHtml ? 'Preview' : 'HTML Source' }}
          </button>
        </div>
        <div v-if="showHtml" class="p-4">
          <pre class="text-xs font-mono text-surface-400 whitespace-pre-wrap">{{ entry.content.html_body }}</pre>
        </div>
        <div v-else class="p-4 bg-white">
          <iframe :srcdoc="entry.content.html_body" class="w-full min-h-64 border-0" sandbox="" />
        </div>
      </div>

      <div v-else-if="entry.content?.body" class="rounded-xl border border-surface-800 light:border-surface-200 p-4">
        <pre class="text-sm text-surface-300 light:text-surface-700 whitespace-pre-wrap">{{ entry.content.body }}</pre>
      </div>
    </div>
  </div>
</template>
