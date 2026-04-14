<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchConfirmations, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type PortalOrderStatus = 'pending' | 'pending_payment' | 'paid' | 'pending_shipment' | 'shipped' | 'completed'

interface PortalOrderRow {
  orderNo: string
  orderDate: string
  amount: string
  currency: string
  eta: string
  status: PortalOrderStatus
  confirmationRate: string
}

const { t } = useI18n()

const keyword = ref('')
const statusFilter = ref<'all' | PortalOrderStatus>('all')

const rows = ref<PortalOrderRow[]>([])

onMounted(async () => {
  try {
    const [orderRows, confirmationRows] = await Promise.all([fetchOrders(), fetchConfirmations()])
    const confirmCountMap = confirmationRows.reduce<Record<string, { done: number; total: number }>>((acc, item) => {
      const key = item.order_no || ''
      if (!key) {
        return acc
      }
      if (!acc[key]) {
        acc[key] = { done: 0, total: 0 }
      }
      acc[key].total += 1
      if (item.status === 'approved') {
        acc[key].done += 1
      }
      return acc
    }, {})

    rows.value = orderRows.map((item) => {
      const progress = confirmCountMap[item.order_no]
      const ratio = progress ? `${Math.round((progress.done / Math.max(progress.total, 1)) * 100)}%` : '0%'
      return {
        orderNo: item.order_no,
        orderDate: item.order_date,
        amount: item.amount,
        currency: item.currency,
        eta: item.eta || '-',
        status: item.status,
        confirmationRate: ratio,
      }
    })
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
  { value: 'all', label: t('portalOrders.filters.all') },
  { value: 'pending', label: t('order.status.pending') },
  { value: 'pending_payment', label: t('order.status.pending_payment') },
  { value: 'paid', label: t('order.status.paid') },
  { value: 'pending_shipment', label: t('order.status.pending_shipment') },
  { value: 'shipped', label: t('order.status.shipped') },
  { value: 'completed', label: t('order.status.completed') },
])

const filteredRows = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const matchKeyword = !q || `${item.orderNo} ${item.amount}`.toLowerCase().includes(q)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: PortalOrderStatus) {
  return t(`order.status.${status}`)
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'orders' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('portalOrders.kicker') }}</p>
          <h1>{{ t('portalOrders.title') }}</h1>
          <p>{{ t('portalOrders.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('portalOrders.actions.export') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="keyword" class="dashboard-search" :placeholder="t('portalOrders.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('portalOrders.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('order.columns.orderNo') }}</th>
              <th>{{ t('order.columns.orderDate') }}</th>
              <th>{{ t('order.columns.amount') }}</th>
              <th>{{ t('order.columns.currency') }}</th>
              <th>{{ t('order.columns.eta') }}</th>
              <th>{{ t('order.columns.confirmationRate') }}</th>
              <th>{{ t('order.columns.status') }}</th>
              <th>{{ t('order.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="item.orderNo">
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.orderDate }}</td>
              <td>{{ item.amount }}</td>
              <td>{{ item.currency }}</td>
              <td>{{ item.eta }}</td>
              <td>{{ item.confirmationRate }}</td>
              <td>
                <span class="status-tag" :class="`order-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>
                <button class="text-button" type="button">{{ t('portalOrders.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
