export interface TelescopeEntry {
  uuid: string
  batch_id: string | null
  type: number
  type_label: string
  type_slug: string
  summary: string
  content: Record<string, any>
  tags: string[]
  created_at: string
}

export interface EntryListResponse {
  entries: TelescopeEntry[]
  has_more: boolean
  type?: {
    value: number
    label: string
    slug: string
  }
}

export interface EntryDetailResponse {
  entry: TelescopeEntry
}

export interface StatusResponse {
  enabled: boolean
  recording: boolean
  total_entries: number
  types: Record<string, { label: string; count: number }>
}

export interface BatchResponse {
  entries: TelescopeEntry[]
  batch_id: string
}

export type EntryTypeSlug =
  | 'request' | 'query' | 'exception' | 'model' | 'log'
  | 'cache' | 'redis' | 'mail' | 'view' | 'event'
  | 'command' | 'dump' | 'client-request' | 'gate'
  | 'notification' | 'schedule' | 'batch'

export interface NavItem {
  slug: EntryTypeSlug
  label: string
  icon: string
}
