import { ref } from 'vue'
import type { TelescopeEntry } from './types'

export type WsStatus = 'connecting' | 'connected' | 'disconnected'

const WS_RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000]

export function useWebSocket() {
  const status = ref<WsStatus>('disconnected')
  const lastEntry = ref<TelescopeEntry | null>(null)

  let ws: WebSocket | null = null
  let reconnectAttempt = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let listeners: Array<(entry: TelescopeEntry) => void> = []

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    const config = window.__TELESCOPE_CONFIG__ || {
      wsUrl: `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/telescope/`,
    }

    status.value = 'connecting'
    ws = new WebSocket(config.wsUrl)

    ws.onopen = () => {
      status.value = 'connected'
      reconnectAttempt = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'entry' && data.data) {
          lastEntry.value = data.data
          listeners.forEach(fn => fn(data.data))
        }
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      status.value = 'disconnected'
      ws = null
      scheduleReconnect()
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function scheduleReconnect() {
    if (reconnectTimer) return
    const delay = WS_RECONNECT_DELAYS[Math.min(reconnectAttempt, WS_RECONNECT_DELAYS.length - 1)]
    reconnectAttempt++
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null
      connect()
    }, delay)
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    ws?.close()
    ws = null
    status.value = 'disconnected'
  }

  function onEntry(callback: (entry: TelescopeEntry) => void) {
    listeners.push(callback)
    return () => {
      listeners = listeners.filter(fn => fn !== callback)
    }
  }

  function sendFilter(filters: { types?: string[] }) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'filter', filters }))
    }
  }

  return { status, lastEntry, connect, disconnect, onEntry, sendFilter }
}

// Singleton instance
let _instance: ReturnType<typeof useWebSocket> | null = null

export function getWebSocket() {
  if (!_instance) {
    _instance = useWebSocket()
  }
  return _instance
}
