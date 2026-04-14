<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchCustomers, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type CustomerStatus = 'enabled' | 'disabled'

interface CustomerRow {
  id: string
  companyName: string
  contactName: string
  email: string
  phone: string
  region: string
  status: CustomerStatus
  orderCount: number
  updatedAt: string
}

const { t } = useI18n()

const search = ref('')
const statusFilter = ref<'all' | CustomerStatus>('all')

const customers = ref<CustomerRow[]>([])

function formatTime(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(async () => {
  try {
    const [customerRows, orderRows] = await Promise.all([fetchCustomers(), fetchOrders()])
    const orderCountMap = orderRows.reduce<Record<number, number>>((acc, item) => {
      const customerId = item.customer
      if (customerId) {
        acc[customerId] = (acc[customerId] || 0) + 1
      }
      return acc
    }, {})

    customers.value = customerRows.map((item) => ({
      id: `CUST-${String(item.id).padStart(3, '0')}`,
      companyName: item.company_name,
      contactName: item.contact_name,
      email: item.contact_email,
      phone: item.contact_phone,
      region: item.region,
      status: item.status,
      orderCount: orderCountMap[item.id] || 0,
      updatedAt: formatTime(item.updated_at),
    }))
  } catch {
    customers.value = []
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
  { value: 'all', label: t('customer.filters.all') },
  { value: 'enabled', label: t('customer.status.enabled') },
  { value: 'disabled', label: t('customer.status.disabled') },
])

const filteredCustomers = computed(() => {
  const keyword = search.value.toLowerCase().trim()
  return customers.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const haystack = `${item.companyName} ${item.contactName} ${item.email} ${item.id}`.toLowerCase()
    const matchKeyword = !keyword || haystack.includes(keyword)
    return matchStatus && matchKeyword
  })
})

function statusLabel(status: CustomerStatus) {
  return status === 'enabled' ? t('customer.status.enabled') : t('customer.status.disabled')
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'customers' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('customer.kicker') }}</p>
          <h1>{{ t('customer.title') }}</h1>
          <p>{{ t('customer.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('customer.actions.import') }}</button>
          <button class="primary-button">{{ t('customer.actions.create') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="search" class="dashboard-search" :placeholder="t('customer.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredCustomers.length }}</strong>
          <span>{{ t('customer.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('customer.columns.id') }}</th>
              <th>{{ t('customer.columns.companyName') }}</th>
              <th>{{ t('customer.columns.contactName') }}</th>
              <th>{{ t('customer.columns.email') }}</th>
              <th>{{ t('customer.columns.phone') }}</th>
              <th>{{ t('customer.columns.region') }}</th>
              <th>{{ t('customer.columns.orderCount') }}</th>
              <th>{{ t('customer.columns.status') }}</th>
              <th>{{ t('customer.columns.updatedAt') }}</th>
              <th>{{ t('customer.columns.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredCustomers" :key="item.id">
              <td class="mono">{{ item.id }}</td>
              <td>{{ item.companyName }}</td>
              <td>{{ item.contactName }}</td>
              <td>{{ item.email }}</td>
              <td>{{ item.phone }}</td>
              <td>{{ item.region }}</td>
              <td>{{ item.orderCount }}</td>
              <td>
                <span class="status-tag" :class="item.status">{{ statusLabel(item.status) }}</span>
              </td>
              <td>{{ item.updatedAt }}</td>
              <td>
                <button class="text-button" type="button">{{ t('customer.actions.view') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </section>
  </main>
</template>
