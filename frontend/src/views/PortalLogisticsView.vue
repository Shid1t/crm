<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchLogistics } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type PortalShipStatus = 'preparing' | 'inTransit' | 'customs' | 'delayed' | 'delivered'

interface PortalShipRow {
  orderNo: string
  trackingNo: string
  etd: string
  eta: string
  status: PortalShipStatus
  latestNote: string
}

const { t } = useI18n()

const keyword = ref('')
const statusFilter = ref<'all' | PortalShipStatus>('all')

const rows = ref<PortalShipRow[]>([])

onMounted(async () => {
  try {
    const data = await fetchLogistics()
    rows.value = data.map((item) => ({
      orderNo: item.order_no || '-',
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
  { key: 'home', label: t('portal.menu.home'), to: '/portal/home' },
  { key: 'orders', label: t('portal.menu.orders'), to: '/portal/orders' },
  { key: 'confirmations', label: t('portal.menu.confirmations'), to: '/portal/confirmations' },
  { key: 'files', label: t('portal.menu.files'), to: '/portal/files' },
  { key: 'logistics', label: t('portal.menu.logistics'), to: '/portal/logistics' },
  { key: 'messages', label: t('portal.menu.messages'), to: '/portal/messages' },
  { key: 'account', label: t('portal.menu.account'), to: '/portal/account' },
])

const statusOptions = computed(() => [
  { value: 'all', label: t('portalLogistics.filters.all') },
  { value: 'preparing', label: t('logistics.status.preparing') },
  { value: 'inTransit', label: t('logistics.status.inTransit') },
  { value: 'customs', label: t('logistics.status.customs') },
  { value: 'delayed', label: t('logistics.status.delayed') },
  { value: 'delivered', label: t('logistics.status.delivered') },
])

const filteredRows = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const matchKeyword = !q || `${item.orderNo} ${item.trackingNo} ${item.latestNote}`.toLowerCase().includes(q)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: PortalShipStatus) {
  return t(`logistics.status.${status}`)
}
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
          <p class="panel-kicker">{{ t('portalLogistics.kicker') }}</p>
          <h1>{{ t('portalLogistics.title') }}</h1>
          <p>{{ t('portalLogistics.subtitle') }}</p>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="keyword" class="dashboard-search" :placeholder="t('portalLogistics.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('portalLogistics.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('logistics.columns.orderNo') }}</th>
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
              <td class="mono">{{ item.trackingNo }}</td>
              <td>{{ item.etd }}</td>
              <td>{{ item.eta }}</td>
              <td>
                <span class="status-tag" :class="`ship-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>{{ item.latestNote }}</td>
              <td>
                <button class="text-button" type="button">{{ t('portalLogistics.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
