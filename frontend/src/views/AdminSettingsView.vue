<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import LocaleSwitch from '../components/LocaleSwitch.vue'
import { fetchUsers } from '../api/resources'
import type { UserDTO } from '../api/resources'

const { t } = useI18n()

interface UserRow {
  id: number
  username: string
  email: string
  role: 'admin' | 'customer'
  customer: number | null
  customerName: string
  isEnabled: boolean
  lastLogin: string
}

const users = ref<UserRow[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const data = await fetchUsers()
    users.value = data.map((u: UserDTO) => ({
      id: u.id,
      username: u.username,
      email: u.email,
      role: u.role,
      customer: u.customer,
      customerName: u.customer_name || '-',
      isEnabled: u.is_enabled,
      lastLogin: u.last_login ? new Date(u.last_login).toLocaleString() : '-',
    }))
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
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
  { key: 'settings', label: t('dashboard.menus.settings'), to: '/admin/settings', active: true },
])

const activeCount = computed(() => users.value.filter(u => u.isEnabled).length)
const inactiveCount = computed(() => users.value.filter(u => !u.isEnabled).length)
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
          <RouterLink
            v-if="item.to"
            class="nav-item"
            :class="{ active: item.active }"
            :to="item.to"
          >
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
          <p class="panel-kicker">{{ t('settings.kicker') }}</p>
          <h1>{{ t('settings.title') }}</h1>
          <p>{{ t('settings.subtitle') }}</p>
        </div>
      </header>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <p>{{ t('common.loading') }}</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
      </div>

      <template v-else>
        <section class="dashboard-grid dashboard-grid-metrics">
          <article class="dashboard-card metric-card">
            <span class="card-label">{{ t('settings.userColumns.status') }}</span>
            <strong>{{ activeCount }}</strong>
            <span class="trend-tag">{{ t('settings.status.active') }}</span>
          </article>
          <article class="dashboard-card metric-card">
            <span class="card-label">{{ t('settings.userColumns.status') }}</span>
            <strong>{{ inactiveCount }}</strong>
            <span class="trend-tag">{{ t('settings.status.inactive') }}</span>
          </article>
        </section>

        <section class="dashboard-card customer-table-wrap">
          <div class="card-head">
            <h2>{{ t('settings.sections.users') }}</h2>
          </div>
          <table class="customer-table">
            <thead>
              <tr>
                <th>{{ t('settings.userColumns.username') }}</th>
                <th>{{ t('settings.userColumns.email') }}</th>
                <th>{{ t('settings.userColumns.role') }}</th>
                <th>{{ t('settings.userColumns.customer') }}</th>
                <th>{{ t('settings.userColumns.status') }}</th>
                <th>{{ t('settings.userColumns.lastLogin') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td class="mono">{{ user.username }}</td>
                <td>{{ user.email || '-' }}</td>
                <td>
                  <span :class="['status-tag', user.role === 'admin' ? 'order-shipped' : 'order-pending']">
                    {{ t(`settings.roles.${user.role}`) }}
                  </span>
                </td>
                <td>{{ user.customerName }}</td>
                <td>
                  <span :class="['status-tag', user.isEnabled ? 'status-approved' : 'status-revise']">
                    {{ user.isEnabled ? t('settings.status.active') : t('settings.status.inactive') }}
                  </span>
                </td>
                <td>{{ user.lastLogin }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>
    </section>
  </main>
</template>