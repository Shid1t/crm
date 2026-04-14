<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchConfirmations, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type ConfirmStatus = 'pending' | 'approved' | 'revise' | 'resubmitted'

interface ConfirmRow {
  taskNo: string
  orderNo: string
  customerName: string
  itemType: string
  itemName: string
  owner: string
  latestAt: string
  status: ConfirmStatus
}

const { t } = useI18n()

const search = ref('')
const statusFilter = ref<'all' | ConfirmStatus>('all')

const rows = ref<ConfirmRow[]>([])

onMounted(async () => {
  try {
    const [confirmationRows, orderRows] = await Promise.all([fetchConfirmations(), fetchOrders()])
    const orderMap = orderRows.reduce<Record<string, string>>((acc, item) => {
      acc[item.order_no] = item.customer_name || '-'
      return acc
    }, {})

    rows.value = confirmationRows.map((item) => ({
      taskNo: item.task_no,
      orderNo: item.order_no || '-',
      customerName: orderMap[item.order_no || ''] || '-',
      itemType: item.item_type,
      itemName: item.item_name,
      owner: '-',
      latestAt: new Date(item.updated_at).toLocaleString(),
      status: item.status,
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
  { value: 'all', label: t('confirmation.filters.all') },
  { value: 'pending', label: t('confirmation.status.pending') },
  { value: 'approved', label: t('confirmation.status.approved') },
  { value: 'revise', label: t('confirmation.status.revise') },
  { value: 'resubmitted', label: t('confirmation.status.resubmitted') },
])

const filteredRows = computed(() => {
  const keyword = search.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const haystack = `${item.taskNo} ${item.orderNo} ${item.customerName} ${item.itemName}`.toLowerCase()
    const matchKeyword = !keyword || haystack.includes(keyword)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: ConfirmStatus) {
  return t(`confirmation.status.${status}`)
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'confirmations' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('confirmation.kicker') }}</p>
          <h1>{{ t('confirmation.title') }}</h1>
          <p>{{ t('confirmation.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('confirmation.actions.batchExport') }}</button>
          <button class="primary-button">{{ t('confirmation.actions.create') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="search" class="dashboard-search" :placeholder="t('confirmation.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('confirmation.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('confirmation.columns.taskNo') }}</th>
              <th>{{ t('confirmation.columns.orderNo') }}</th>
              <th>{{ t('confirmation.columns.customerName') }}</th>
              <th>{{ t('confirmation.columns.itemType') }}</th>
              <th>{{ t('confirmation.columns.itemName') }}</th>
              <th>{{ t('confirmation.columns.owner') }}</th>
              <th>{{ t('confirmation.columns.latestAt') }}</th>
              <th>{{ t('confirmation.columns.status') }}</th>
              <th>{{ t('confirmation.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="item.taskNo">
              <td class="mono">{{ item.taskNo }}</td>
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.customerName }}</td>
              <td>{{ item.itemType }}</td>
              <td>{{ item.itemName }}</td>
              <td>{{ item.owner }}</td>
              <td>{{ item.latestAt }}</td>
              <td>
                <span class="status-tag" :class="`confirm-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>
                <button class="text-button" type="button">{{ t('confirmation.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
