<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchFiles } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type PortalFileType = 'PI' | 'Contract' | 'Artwork' | 'Shipping'

interface PortalFileRow {
  fileName: string
  orderNo: string
  fileType: PortalFileType
  version: string
  size: string
  uploadedAt: string
}

const { t } = useI18n()

const keyword = ref('')
const typeFilter = ref<'all' | PortalFileType>('all')

const rows = ref<PortalFileRow[]>([])

onMounted(async () => {
  try {
    const data = await fetchFiles()
    rows.value = data
      .filter((item) => item.visibility === 'customer')
      .map((item) => ({
        fileName: item.file_name,
        orderNo: item.order_no || '-',
        fileType: item.file_type as PortalFileType,
        version: item.version,
        size: item.size,
        uploadedAt: new Date(item.uploaded_at).toLocaleString(),
      }))
  } catch {
    rows.value = []
  }
})

const menuItems = computed(() => [
  { key: 'home', label: t('portal.menu.home'), to: '/portal/home' },
  { key: 'orders', label: t('portal.menu.orders'), to: '/portal/orders' },
  { key: 'confirmations', label: t('portal.menu.confirmations'), to: '/portal/confirmations' },
  { key: 'files', label: t('portal.menu.files'), to: '/portal/files' },
  { key: 'logistics', label: t('portal.menu.logistics'), to: '/portal/logistics' },
  { key: 'messages', label: t('portal.menu.messages'), to: '/portal/messages' },
  { key: 'account', label: t('portal.menu.account'), to: '/portal/account' },
])

const typeOptions = computed(() => [
  { value: 'all', label: t('portalFiles.filters.all') },
  { value: 'PI', label: t('portalFiles.filters.fileTypes.PI') },
  { value: 'Contract', label: t('portalFiles.filters.fileTypes.Contract') },
  { value: 'Artwork', label: t('portalFiles.filters.fileTypes.Artwork') },
  { value: 'Shipping', label: t('portalFiles.filters.fileTypes.Shipping') },
  { value: 'PL', label: t('portalFiles.filters.fileTypes.PL') },
  { value: 'BL', label: t('portalFiles.filters.fileTypes.BL') },
  { value: 'CI', label: t('portalFiles.filters.fileTypes.CI') },
  { value: 'DL', label: t('portalFiles.filters.fileTypes.DL') },
  { value: 'MSDS', label: t('portalFiles.filters.fileTypes.MSDS') },
  { value: 'CERT', label: t('portalFiles.filters.fileTypes.CERT') },
])

const filteredRows = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchType = typeFilter.value === 'all' || item.fileType === typeFilter.value
    const matchKeyword = !q || `${item.fileName} ${item.orderNo}`.toLowerCase().includes(q)
    return matchType && matchKeyword
  })
})
</script>

<template>
  <main class="dashboard-shell portal-shell">
    <aside class="dashboard-sidebar portal-sidebar">
      <div class="sidebar-brand">
        <span class="brand-mark" />
        <div>
          <strong>{{ t('portal.systemName') }}</strong>
          <p>{{ t('portal.role') }}</p>
        </div>
      </div>

      <nav class="sidebar-nav">
        <template v-for="item in menuItems" :key="item.key">
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'files' }" :to="item.to">
            {{ item.label }}
          </RouterLink>
          <button v-else class="nav-item" type="button">{{ item.label }}</button>
        </template>
      </nav>

      <div class="sidebar-footer">
        <LocaleSwitch />
      </div>
    </aside>

    <section class="dashboard-main">
      <header class="dashboard-header">
        <div>
          <p class="panel-kicker">{{ t('portalFiles.kicker') }}</p>
          <h1>{{ t('portalFiles.title') }}</h1>
          <p>{{ t('portalFiles.subtitle') }}</p>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="keyword" class="dashboard-search" :placeholder="t('portalFiles.filters.keywordPlaceholder')" type="text" />

        <select v-model="typeFilter" class="customer-select">
          <option v-for="option in typeOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('portalFiles.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('fileCenter.columns.fileName') }}</th>
              <th>{{ t('fileCenter.columns.orderNo') }}</th>
              <th>{{ t('fileCenter.columns.fileType') }}</th>
              <th>{{ t('fileCenter.columns.version') }}</th>
              <th>{{ t('fileCenter.columns.size') }}</th>
              <th>{{ t('fileCenter.columns.uploadedAt') }}</th>
              <th>{{ t('fileCenter.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="`${item.fileName}-${item.version}`">
              <td class="mono">{{ item.fileName }}</td>
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.fileType }}</td>
              <td>{{ item.version }}</td>
              <td>{{ item.size }}</td>
              <td>{{ item.uploadedAt }}</td>
              <td>
                <button class="text-button" type="button">{{ t('portalFiles.actions.download') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
