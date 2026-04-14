<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchCurrentUser } from '../api/auth'
import { fetchConfirmations, fetchCustomers, fetchLogistics, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

const { t, locale } = useI18n()
const router = useRouter()

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
const totalOrderCount = computed(() =>
  Object.values(progressValues.value).reduce((sum, current) => sum + current, 0),
)

const progressItems = computed(() => [
  {
    key: 'waiting',
    label: t('dashboard.progress.waiting'),
    value: progressValues.value.waiting,
    ratio: totalOrderCount.value > 0 ? Math.round((progressValues.value.waiting / totalOrderCount.value) * 100) : 0,
  },
  {
    key: 'confirmed',
    label: t('dashboard.progress.confirmed'),
    value: progressValues.value.confirmed,
    ratio: totalOrderCount.value > 0 ? Math.round((progressValues.value.confirmed / totalOrderCount.value) * 100) : 0,
  },
  {
    key: 'production',
    label: t('dashboard.progress.production'),
    value: progressValues.value.production,
    ratio: totalOrderCount.value > 0 ? Math.round((progressValues.value.production / totalOrderCount.value) * 100) : 0,
  },
  {
    key: 'shipped',
    label: t('dashboard.progress.shipped'),
    value: progressValues.value.shipped,
    ratio: totalOrderCount.value > 0 ? Math.round((progressValues.value.shipped / totalOrderCount.value) * 100) : 0,
  },
  {
    key: 'done',
    label: t('dashboard.progress.done'),
    value: progressValues.value.done,
    ratio: totalOrderCount.value > 0 ? Math.round((progressValues.value.done / totalOrderCount.value) * 100) : 0,
  },
])

const logisticsItems = ref<{ code: string; status: string; detail: string }[]>([])
const accountName = ref('')
const currentTimeText = ref('')
let timer: number | null = null

const activityItems = computed(() => [
  { time: '09:20', text: t('dashboard.activity.created') },
  { time: '11:05', text: t('dashboard.activity.revised') },
  { time: '14:40', text: t('dashboard.activity.uploaded') },
])

function updateCurrentTime() {
  const formatter = new Intl.DateTimeFormat(locale.value, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
  currentTimeText.value = formatter.format(new Date())
}

function logout() {
  localStorage.removeItem('crm-access-token')
  localStorage.removeItem('crm-refresh-token')
  localStorage.removeItem('crm-user-role')
  void router.push('/login')
}

onMounted(async () => {
  updateCurrentTime()
  timer = window.setInterval(updateCurrentTime, 1000)

  try {
    const [customers, orders, confirmations, logistics] = await Promise.all([
      fetchCustomers(),
      fetchOrders(),
      fetchConfirmations(),
      fetchLogistics(),
    ])

    try {
      const currentUser = await fetchCurrentUser()
      accountName.value = currentUser.display_name || currentUser.username
    } catch {
      accountName.value = t('dashboard.user.unknown')
    }

    const delivered = logistics.filter((item) => item.status === 'delivered').length
    const onTimeRate = logistics.length ? `${Math.round((delivered / logistics.length) * 100)}%` : '0%'

    metricValues.value = {
      activeCustomers: String(customers.length),
      pendingOrders: String(confirmations.filter((item) => item.status === 'pending').length),
      inProduction: String(orders.filter((item) => item.status === 'pending_shipment').length),
      onTimeRate,
    }

    progressValues.value = {
      waiting: orders.filter((item) => item.status === 'pending').length,
      confirmed: orders.filter((item) => item.status === 'pending_payment').length,
      production: orders.filter((item) => item.status === 'paid').length,
      shipped: orders.filter((item) => item.status === 'shipped').length,
      done: orders.filter((item) => item.status === 'completed').length,
    }

    logisticsItems.value = logistics.map((item) => ({
      code: item.tracking_no,
      status: t(`logistics.status.${item.status}`),
      detail: item.eta || '-',
    }))
  } catch {
    metricValues.value = { activeCustomers: '0', pendingOrders: '0', inProduction: '0', onTimeRate: '0%' }
    progressValues.value = { waiting: 0, confirmed: 0, production: 0, shipped: 0, done: 0 }
    logisticsItems.value = []
    accountName.value = t('dashboard.user.unknown')
  }
})

onUnmounted(() => {
  if (timer !== null) {
    window.clearInterval(timer)
  }
})

watch(locale, () => {
  updateCurrentTime()
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

        <div class="header-user-panel">
          <div class="header-user-block">
            <span>{{ t('dashboard.user.account') }}</span>
            <strong>{{ accountName || t('dashboard.user.unknown') }}</strong>
          </div>
          <div class="header-user-block">
            <span>{{ t('dashboard.user.currentTime') }}</span>
            <strong>{{ currentTimeText }}</strong>
          </div>
          <button class="secondary-button" type="button" @click="logout">{{ t('dashboard.user.logout') }}</button>
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
            <span class="progress-total">{{ t('dashboard.progress.totalOrders', { total: totalOrderCount }) }}</span>
          </div>

          <div class="progress-list">
            <div v-for="item in progressItems" :key="item.label" class="progress-row" :data-status="item.key">
              <div class="progress-copy">
                <span>{{ item.label }}</span>
                <div class="progress-copy-value">
                  <strong>{{ item.value }}</strong>
                  <em>{{ item.ratio }}%</em>
                </div>
              </div>
              <div class="progress-bar">
                <span :style="{ width: `${item.ratio}%` }" />
              </div>
            </div>
          </div>
        </article>

        <article class="dashboard-card side-card">
          <div class="card-head">
            <h2>{{ t('dashboard.sections.todo') }}</h2>
          </div>

          <div class="todo-list scroll-list">
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

          <div class="logistics-list scroll-list">
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

      </section>
    </section>
  </main>
</template>
