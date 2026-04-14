<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchFiles, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type FileVisibility = 'customer' | 'internal'

interface FileRow {
  fileName: string
  orderNo: string
  customerName: string
  fileType: 'PI' | 'Contract' | 'Artwork' | 'QC' | 'Shipping'
  version: string
  size: string
  uploader: string
  uploadedAt: string
  visibility: FileVisibility
}

const { t } = useI18n()

const search = ref('')
const visibilityFilter = ref<'all' | FileVisibility>('all')

const rows = ref<FileRow[]>([])

onMounted(async () => {
  try {
    const [fileRows, orderRows] = await Promise.all([fetchFiles(), fetchOrders()])
    const orderMap = orderRows.reduce<Record<string, string>>((acc, item) => {
      acc[item.order_no] = item.customer_name || '-'
      return acc
    }, {})

    rows.value = fileRows.map((item) => ({
      fileName: item.file_name,
      orderNo: item.order_no || '-',
      customerName: orderMap[item.order_no || ''] || '-',
      fileType: item.file_type as FileRow['fileType'],
      version: item.version,
      size: item.size,
      uploader: item.uploader_name || '-',
      uploadedAt: new Date(item.uploaded_at).toLocaleString(),
      visibility: item.visibility,
    }))
  } catch {
    rows.value = []
  }
})

const menuItems = computed(() => [
  { key: 'dashboard', label: t('dashboard.menus.dashboard'), to: '/admin/dashboard' },
  { key: 'customers', label: t('dashboard.menus.customers'), to: '/admin/customers' },
  { key: 'orders', label: t('dashboard.menus.orders'), to: '/admin/orders' },
  { key: 'confirmations', label: t('dashboard.menus.confirmations'), to: '/admin/confirmations' },
  { key: 'files', label: t('dashboard.menus.files'), to: '/admin/files' },
  { key: 'logistics', label: t('dashboard.menus.logistics'), to: '/admin/logistics' },
  { key: 'messages', label: t('dashboard.menus.messages'), to: '/admin/messages' },
  { key: 'settings', label: t('dashboard.menus.settings'), to: '/admin/settings' },
])

const visibilityOptions = computed(() => [
  { value: 'all', label: t('fileCenter.filters.allVisibility') },
  { value: 'customer', label: t('fileCenter.visibility.customer') },
  { value: 'internal', label: t('fileCenter.visibility.internal') },
])

const filteredRows = computed(() => {
  const keyword = search.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchVisibility = visibilityFilter.value === 'all' || item.visibility === visibilityFilter.value
    const haystack = `${item.fileName} ${item.orderNo} ${item.customerName} ${item.fileType}`.toLowerCase()
    const matchKeyword = !keyword || haystack.includes(keyword)
    return matchVisibility && matchKeyword
  })
})

function visibilityLabel(visibility: FileVisibility) {
  return visibility === 'customer' ? t('fileCenter.visibility.customer') : t('fileCenter.visibility.internal')
}
</script>

<template>
  <main class="dashboard-shell">
    <aside class="dashboard-sidebar">
      <div class="sidebar-brand">
        <span class="brand-mark" />
        <div>
          <strong>{{ t('dashboard.systemName') }}</strong>
          <p>{{ t('dashboard.role') }}</p>
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
          <p class="panel-kicker">{{ t('fileCenter.kicker') }}</p>
          <h1>{{ t('fileCenter.title') }}</h1>
          <p>{{ t('fileCenter.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('fileCenter.actions.batchDownload') }}</button>
          <button class="primary-button">{{ t('fileCenter.actions.upload') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="search" class="dashboard-search" :placeholder="t('fileCenter.filters.keywordPlaceholder')" type="text" />

        <select v-model="visibilityFilter" class="customer-select">
          <option v-for="option in visibilityOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('fileCenter.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('fileCenter.columns.fileName') }}</th>
              <th>{{ t('fileCenter.columns.orderNo') }}</th>
              <th>{{ t('fileCenter.columns.customerName') }}</th>
              <th>{{ t('fileCenter.columns.fileType') }}</th>
              <th>{{ t('fileCenter.columns.version') }}</th>
              <th>{{ t('fileCenter.columns.size') }}</th>
              <th>{{ t('fileCenter.columns.uploader') }}</th>
              <th>{{ t('fileCenter.columns.uploadedAt') }}</th>
              <th>{{ t('fileCenter.columns.visibility') }}</th>
              <th>{{ t('fileCenter.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="`${item.fileName}-${item.version}`">
              <td class="mono">{{ item.fileName }}</td>
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.customerName }}</td>
              <td>{{ item.fileType }}</td>
              <td>{{ item.version }}</td>
              <td>{{ item.size }}</td>
              <td>{{ item.uploader }}</td>
              <td>{{ item.uploadedAt }}</td>
              <td>
                <span class="status-tag" :class="`file-${item.visibility}`">{{ visibilityLabel(item.visibility) }}</span>
              </td>
              <td>
                <button class="text-button" type="button">{{ t('fileCenter.actions.download') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
