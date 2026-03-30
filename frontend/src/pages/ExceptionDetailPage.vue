<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import type { TelescopeEntry } from '../types'
import KeyValueTable from '../components/KeyValueTable.vue'
import StackTrace from '../components/StackTrace.vue'

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
      ← Back to Exceptions
    </button>

    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-8 w-64"></div>
      <div class="skeleton h-64 w-full rounded-xl"></div>
    </div>

    <div v-else-if="entry" class="space-y-6 animate-fade-in">
      <div>
        <h1 class="text-xl font-bold text-red-400 mb-1">{{ entry.content?.class }}</h1>
        <p class="text-sm text-surface-400 font-mono">{{ entry.content?.message }}</p>
      </div>

      <KeyValueTable
        title="Exception Info"
        :data="{
          'Class': entry.content?.class,
          'Module': entry.content?.module,
          'Message': entry.content?.message,
          'File': entry.content?.file,
          'Line': entry.content?.line,
        }"
      />

      <StackTrace v-if="entry.content?.frames" :frames="entry.content.frames" />
    </div>
  </div>
</template>
