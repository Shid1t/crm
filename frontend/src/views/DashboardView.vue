<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchConfirmations, fetchCustomers, fetchLogistics, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

const { t } = useI18n()

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

const metricValues = ref({
  activeCustomers: '0',
  pendingOrders: '0',
  inProduction: '0',
  onTimeRate: '0%',
})

const metricItems = computed(() => [
  { value: metricValues.value.activeCustomers, label: t('dashboard.metrics.activeCustomers'), trend: '-' },
  { value: metricValues.value.pendingOrders, label: t('dashboard.metrics.pendingOrders'), trend: '-' },
  { value: metricValues.value.inProduction, label: t('dashboard.metrics.inProduction'), trend: '-' },
  { value: metricValues.value.onTimeRate, label: t('dashboard.metrics.onTimeRate'), trend: '-' },
])

const todoItems = computed(() => [
  { level: t('dashboard.todo.urgent'), text: t('dashboard.todo.items.confirm') },
  { level: t('dashboard.todo.high'), text: t('dashboard.todo.items.upload') },
  { level: t('dashboard.todo.normal'), text: t('dashboard.todo.items.shipment') },
])

const progressValues = ref({ waiting: 0, confirmed: 0, production: 0, shipped: 0, done: 0 })

const progressItems = computed(() => [
  { label: t('dashboard.progress.waiting'), value: progressValues.value.waiting },
  { label: t('dashboard.progress.confirmed'), value: progressValues.value.confirmed },
  { label: t('dashboard.progress.production'), value: progressValues.value.production },
  { label: t('dashboard.progress.shipped'), value: progressValues.value.shipped },
  { label: t('dashboard.progress.done'), value: progressValues.value.done },
])

const logisticsItems = ref<{ code: string; status: string; detail: string }[]>([])

const activityItems = computed(() => [
  { time: '09:20', text: t('dashboard.activity.created') },
  { time: '11:05', text: t('dashboard.activity.revised') },
  { time: '14:40', text: t('dashboard.activity.uploaded') },
])

const catalogItems = computed(() => [
  { title: t('dashboard.catalog.tools'), desc: t('dashboard.catalog.toolsDesc') },
  { title: t('dashboard.catalog.machinery'), desc: t('dashboard.catalog.machineryDesc') },
  { title: t('dashboard.catalog.accessories'), desc: t('dashboard.catalog.accessoriesDesc') },
])

onMounted(async () => {
  try {
    const [customers, orders, confirmations, logistics] = await Promise.all([
      fetchCustomers(),
      fetchOrders(),
      fetchConfirmations(),
      fetchLogistics(),
    ])

    const delivered = logistics.filter((item) => item.status === 'delivered').length
    const onTimeRate = logistics.length ? `${Math.round((delivered / logistics.length) * 100)}%` : '0%'

    metricValues.value = {
      activeCustomers: String(customers.length),
      pendingOrders: String(orders.filter((item) => item.status === 'pending').length),
      inProduction: String(orders.filter((item) => item.status === 'production').length),
      onTimeRate,
    }

    progressValues.value = {
      waiting: confirmations.filter((item) => item.status === 'pending').length,
      confirmed: confirmations.filter((item) => item.status === 'approved').length,
      production: orders.filter((item) => item.status === 'production').length,
      shipped: orders.filter((item) => item.status === 'shipped').length,
      done: orders.filter((item) => item.status === 'completed').length,
    }

    logisticsItems.value = logistics.slice(0, 3).map((item) => ({
      code: item.tracking_no,
      status: t(`logistics.status.${item.status}`),
      detail: item.eta || '-',
    }))
  } catch {
    metricValues.value = { activeCustomers: '0', pendingOrders: '0', inProduction: '0', onTimeRate: '0%' }
    progressValues.value = { waiting: 0, confirmed: 0, production: 0, shipped: 0, done: 0 }
    logisticsItems.value = []
  }
})
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'dashboard' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('dashboard.kicker') }}</p>
          <h1>{{ t('dashboard.welcome') }}</h1>
          <p>{{ t('dashboard.overview') }}</p>
        </div>

        <div class="header-actions">
          <input :placeholder="t('dashboard.searchPlaceholder')" class="dashboard-search" type="text" />
          <button class="secondary-button">{{ t('dashboard.secondaryAction') }}</button>
          <button class="primary-button">{{ t('dashboard.primaryAction') }}</button>
        </div>
      </header>

      <section class="dashboard-grid dashboard-grid-metrics">
        <article v-for="item in metricItems" :key="item.label" class="dashboard-card metric-card">
          <span class="card-label">{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <span class="trend-tag">{{ item.trend }}</span>
        </article>
      </section>

      <section class="dashboard-grid dashboard-grid-main">
        <article class="dashboard-card wide-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.progress') }}</h2>
          </div>

          <div class="progress-list">
            <div v-for="item in progressItems" :key="item.label" class="progress-row">
              <div class="progress-copy">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
              <div class="progress-bar">
                <span :style="{ width: `${Math.min(item.value, 100)}%` }" />
              </div>
            </div>
          </div>
        </article>

        <article class="dashboard-card side-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.todo') }}</h2>
          </div>

          <div class="todo-list">
            <div v-for="item in todoItems" :key="item.text" class="todo-item">
              <span class="todo-level">{{ item.level }}</span>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </article>

        <article class="dashboard-card side-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.logistics') }}</h2>
          </div>

          <div class="logistics-list">
            <div v-for="item in logisticsItems" :key="item.code" class="logistics-item">
              <strong>{{ item.code }}</strong>
              <span>{{ item.status }}</span>
              <em>{{ item.detail }}</em>
            </div>
          </div>
        </article>

        <article class="dashboard-card side-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.activity') }}</h2>
          </div>

          <div class="activity-list">
            <div v-for="item in activityItems" :key="`${item.time}-${item.text}`" class="activity-item">
              <span>{{ item.time }}</span>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </article>

        <article class="dashboard-card wide-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.catalog') }}</h2>
          </div>

          <div class="catalog-grid">
            <div v-for="item in catalogItems" :key="item.title" class="catalog-item">
              <span class="catalog-mark" />
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>
