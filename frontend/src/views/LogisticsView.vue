<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchLogistics, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type ShipStatus = 'preparing' | 'inTransit' | 'customs' | 'delayed' | 'delivered'

interface LogisticsRow {
  orderNo: string
  customerName: string
  company: string
  trackingNo: string
  etd: string
  eta: string
  status: ShipStatus
  latestNote: string
}

const { t } = useI18n()

const search = ref('')
const statusFilter = ref<'all' | ShipStatus>('all')

const rows = ref<LogisticsRow[]>([])

onMounted(async () => {
  try {
    const [logRows, orderRows] = await Promise.all([fetchLogistics(), fetchOrders()])
    const orderMap = orderRows.reduce<Record<string, string>>((acc, item) => {
      acc[item.order_no] = item.customer_name || '-'
      return acc
    }, {})
    rows.value = logRows.map((item) => ({
      orderNo: item.order_no || '-',
      customerName: orderMap[item.order_no || ''] || '-',
      company: item.company,
      trackingNo: item.tracking_no,
      etd: item.etd || '-',
      eta: item.eta || '-',
      status: item.status,
      latestNote: item.latest_note,
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

const statusOptions = computed(() => [
  { value: 'all', label: t('logistics.filters.all') },
  { value: 'preparing', label: t('logistics.status.preparing') },
  { value: 'inTransit', label: t('logistics.status.inTransit') },
  { value: 'customs', label: t('logistics.status.customs') },
  { value: 'delayed', label: t('logistics.status.delayed') },
  { value: 'delivered', label: t('logistics.status.delivered') },
])

const filteredRows = computed(() => {
  const keyword = search.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const haystack = `${item.orderNo} ${item.customerName} ${item.trackingNo} ${item.company}`.toLowerCase()
    const matchKeyword = !keyword || haystack.includes(keyword)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: ShipStatus) {
  return t(`logistics.status.${status}`)
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'logistics' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('logistics.kicker') }}</p>
          <h1>{{ t('logistics.title') }}</h1>
          <p>{{ t('logistics.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('logistics.actions.sync') }}</button>
          <button class="primary-button">{{ t('logistics.actions.update') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="search" class="dashboard-search" :placeholder="t('logistics.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('logistics.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('logistics.columns.orderNo') }}</th>
              <th>{{ t('logistics.columns.customerName') }}</th>
              <th>{{ t('logistics.columns.company') }}</th>
              <th>{{ t('logistics.columns.trackingNo') }}</th>
              <th>{{ t('logistics.columns.etd') }}</th>
              <th>{{ t('logistics.columns.eta') }}</th>
              <th>{{ t('logistics.columns.status') }}</th>
              <th>{{ t('logistics.columns.latestNote') }}</th>
              <th>{{ t('logistics.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="item.trackingNo">
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.customerName }}</td>
              <td>{{ item.company }}</td>
              <td class="mono">{{ item.trackingNo }}</td>
              <td>{{ item.etd }}</td>
              <td>{{ item.eta }}</td>
              <td>
                <span class="status-tag" :class="`ship-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>{{ item.latestNote }}</td>
              <td>
                <button class="text-button" type="button">{{ t('logistics.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
