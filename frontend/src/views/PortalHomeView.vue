<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { fetchConfirmations, fetchFiles, fetchMessageThreads, fetchOrders } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

const { t } = useI18n()

const menuItems = computed(() => [
  { key: 'home', label: t('portal.menu.home'), to: '/portal/home' },
  { key: 'orders', label: t('portal.menu.orders'), to: '/portal/orders' },
  { key: 'confirmations', label: t('portal.menu.confirmations'), to: '/portal/confirmations' },
  { key: 'files', label: t('portal.menu.files'), to: '/portal/files' },
  { key: 'logistics', label: t('portal.menu.logistics'), to: '/portal/logistics' },
  { key: 'messages', label: t('portal.menu.messages'), to: '/portal/messages' },
  { key: 'account', label: t('portal.menu.account'), to: '/portal/account' },
])

const statValues = ref({
  pendingConfirm: '0',
  activeOrders: '0',
  newFiles: '0',
  unreadMessages: '0',
})

const statCards = computed(() => [
  { value: statValues.value.pendingConfirm, label: t('portal.stats.pendingConfirm') },
  { value: statValues.value.activeOrders, label: t('portal.stats.activeOrders') },
  { value: statValues.value.newFiles, label: t('portal.stats.newFiles') },
  { value: statValues.value.unreadMessages, label: t('portal.stats.unreadMessages') },
])

interface TimelineItem {
  time: string
  text: string
}
const timelineItems = ref<TimelineItem[]>([])

onMounted(async () => {
  try {
    const [confirmations, orders, files, threads] = await Promise.all([
      fetchConfirmations(),
      fetchOrders(),
      fetchFiles(),
      fetchMessageThreads(),
    ])
    statValues.value = {
      pendingConfirm: String(confirmations.filter((item) => item.status !== 'approved').length),
      activeOrders: String(orders.length),
      newFiles: String(files.filter((item) => item.visibility === 'customer').length),
      unreadMessages: String(threads.length),
    }

    timelineItems.value = threads.slice(0, 5).map((thread) => {
      const d = new Date(thread.created_at)
      const timeStr = `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
      return { time: timeStr, text: thread.title }
    })
  } catch {
    statValues.value = {
      pendingConfirm: '0',
      activeOrders: '0',
      newFiles: '0',
      unreadMessages: '0',
    }
  }
})
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'home' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('portal.kicker') }}</p>
          <h1>{{ t('portal.title') }}</h1>
          <p>{{ t('portal.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('portal.actions.contact') }}</button>
          <button class="primary-button">{{ t('portal.actions.viewOrders') }}</button>
        </div>
      </header>

      <section class="dashboard-grid dashboard-grid-metrics">
        <article v-for="card in statCards" :key="card.label" class="dashboard-card metric-card">
          <span class="card-label">{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
        </article>
      </section>

      <section class="portal-grid">
        <article class="dashboard-card detail-card">
          <div class="card-head">
            <h2>{{ t('portal.sections.timeline') }}</h2>
          </div>

          <div class="timeline-list">
            <div v-for="item in timelineItems" :key="`${item.time}-${item.text}`" class="timeline-item">
              <span>{{ item.time }}</span>
              <p>{{ item.text }}</p>
            </div>
            <div v-if="timelineItems.length === 0" class="empty-state">
              <p>{{ t('common.noData') }}</p>
            </div>
          </div>
        </article>

        <article class="dashboard-card detail-card portal-hero-card">
          <div class="card-head">
            <h2>{{ t('portal.sections.industry') }}</h2>
          </div>

          <p>{{ t('portal.industryDesc') }}</p>
        </article>
      </section>
    </section>
  </main>
</template>
