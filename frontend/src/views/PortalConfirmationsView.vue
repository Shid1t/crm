<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchConfirmations } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type PortalConfirmStatus = 'pending' | 'approved' | 'revise' | 'resubmitted'

interface PortalConfirmRow {
  taskNo: string
  orderNo: string
  itemType: string
  itemName: string
  latestAt: string
  status: PortalConfirmStatus
}

const { t } = useI18n()

const keyword = ref('')
const statusFilter = ref<'all' | PortalConfirmStatus>('all')

const rows = ref<PortalConfirmRow[]>([])

onMounted(async () => {
  try {
    const data = await fetchConfirmations()
    rows.value = data.map((item) => ({
      taskNo: item.task_no,
      orderNo: item.order_no || '-',
      itemType: item.item_type,
      itemName: item.item_name,
      latestAt: new Date(item.updated_at).toLocaleString(),
      status: item.status,
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
  { value: 'all', label: t('portalConfirmations.filters.all') },
  { value: 'pending', label: t('confirmation.status.pending') },
  { value: 'approved', label: t('confirmation.status.approved') },
  { value: 'revise', label: t('confirmation.status.revise') },
  { value: 'resubmitted', label: t('confirmation.status.resubmitted') },
])

const filteredRows = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return rows.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const matchKeyword = !q || `${item.taskNo} ${item.orderNo} ${item.itemName}`.toLowerCase().includes(q)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: PortalConfirmStatus) {
  return t(`confirmation.status.${status}`)
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
          <p class="panel-kicker">{{ t('portalConfirmations.kicker') }}</p>
          <h1>{{ t('portalConfirmations.title') }}</h1>
          <p>{{ t('portalConfirmations.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('portalConfirmations.actions.filter') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="keyword" class="dashboard-search" :placeholder="t('portalConfirmations.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredRows.length }}</strong>
          <span>{{ t('portalConfirmations.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('confirmation.columns.taskNo') }}</th>
              <th>{{ t('confirmation.columns.orderNo') }}</th>
              <th>{{ t('confirmation.columns.itemType') }}</th>
              <th>{{ t('confirmation.columns.itemName') }}</th>
              <th>{{ t('confirmation.columns.latestAt') }}</th>
              <th>{{ t('confirmation.columns.status') }}</th>
              <th>{{ t('confirmation.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredRows" :key="item.taskNo">
              <td class="mono">{{ item.taskNo }}</td>
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.itemType }}</td>
              <td>{{ item.itemName }}</td>
              <td>{{ item.latestAt }}</td>
              <td>
                <span class="status-tag" :class="`confirm-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>
                <button class="text-button" type="button">{{ t('portalConfirmations.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
