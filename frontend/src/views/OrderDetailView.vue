<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

import LocaleSwitch from '../components/LocaleSwitch.vue'
import { fetchOrders, fetchConfirmations, fetchFiles, fetchLogistics, fetchMessageThreads, fetchOrderItems } from '../api/resources'
import type { OrderDTO, ConfirmationDTO, FileDTO, LogisticsDTO, MessageThreadDTO, OrderItemDTO } from '../api/resources'

const route = useRoute()
const { t } = useI18n()

const orderNo = computed(() => String(route.params.orderNo || 'SO-000000'))

const order = ref<OrderDTO | null>(null)
const items = ref<OrderItemDTO[]>([])
const confirmations = ref<ConfirmationDTO[]>([])
const files = ref<FileDTO[]>([])
const logistics = ref<LogisticsDTO[]>([])
const threads = ref<MessageThreadDTO[]>([])
const loading = ref(true)
const error = ref('')

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [orderRes, itemsRes, confRes, fileRes, logRes, threadRes] = await Promise.all([
      fetchOrders({ order_no: orderNo.value }),
      fetchOrderItems({ order_no: orderNo.value }),
      fetchConfirmations({ order_no: orderNo.value }),
      fetchFiles({ order_no: orderNo.value }),
      fetchLogistics({ order_no: orderNo.value }),
      fetchMessageThreads({ order_no: orderNo.value }),
    ])
    order.value = orderRes[0] || null
    items.value = itemsRes
    confirmations.value = confRes
    files.value = fileRes
    logistics.value = logRes
    threads.value = threadRes
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch(orderNo, loadData)

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

const basicInfo = computed(() => {
  if (!order.value) return []
  return [
    { key: t('orderDetail.basic.customer'), value: order.value.customer_name || '-' },
    { key: t('orderDetail.basic.orderDate'), value: order.value.order_date },
    { key: t('orderDetail.basic.currency'), value: order.value.currency },
    { key: t('orderDetail.basic.amount'), value: Number(order.value.amount).toLocaleString() },
    { key: t('orderDetail.basic.eta'), value: order.value.eta || '-' },
    { key: t('orderDetail.basic.status'), value: t(`order.status.${order.value.status}`) },
  ]
})

const confirmationStatusClass = (status: string) => {
  const map: Record<string, string> = {
    pending: 'status-pending',
    approved: 'status-approved',
    revise: 'status-revise',
    resubmitted: 'status-resubmitted',
  }
  return map[status] || ''
}

const fileVisibilityLabel = (v: string) => {
  return v === 'customer' ? t('orderDetail.visibility.customer') : t('orderDetail.visibility.internal')
}

const logisticsStatusLabel = (s: string) => {
  const map: Record<string, string> = {
    preparing: t('logistics.status.preparing'),
    inTransit: t('logistics.status.inTransit'),
    customs: t('logistics.status.customs'),
    delayed: t('logistics.status.delayed'),
    delivered: t('logistics.status.delivered'),
  }
  return map[s] || s
}

const formatDate = (d: string | null) => d ? d.split('T')[0] : '-'
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
          <p class="panel-kicker">{{ t('orderDetail.kicker') }}</p>
          <h1>{{ t('orderDetail.title') }} - {{ orderNo }}</h1>
          <p>{{ t('orderDetail.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <RouterLink class="secondary-button button-link" to="/admin/orders">{{ t('orderDetail.actions.back') }}</RouterLink>
          <button class="primary-button" type="button">{{ t('orderDetail.actions.update') }}</button>
        </div>
      </header>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <p>{{ t('common.loading') }}</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="primary-button" @click="loadData">{{ t('common.retry') }}</button>
      </div>

      <template v-else-if="order">
        <section class="detail-grid">
          <article class="dashboard-card detail-card">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.basic') }}</h2>
            </div>
            <div class="kv-grid">
              <div v-for="row in basicInfo" :key="row.key" class="kv-row">
                <span>{{ row.key }}</span>
                <strong>{{ row.value }}</strong>
              </div>
            </div>
          </article>

          <article class="dashboard-card detail-card detail-span-2">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.items') || 'Product Items' }}</h2>
            </div>
            <div class="detail-table-wrap">
              <table class="detail-table">
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th>Product Name</th>
                    <th>Specification</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in items" :key="item.id">
                    <td class="mono">{{ item.sku }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ item.spec }}</td>
                    <td>{{ item.qty }}</td>
                    <td>{{ order?.currency }} {{ Number(item.unit_price).toFixed(2) }}</td>
                    <td>{{ Number(item.total).toLocaleString() }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="items.length === 0" class="empty-state">
                <p>{{ t('common.noData') }}</p>
              </div>
            </div>
          </article>

          <article class="dashboard-card detail-card detail-span-2">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.confirmation') }}</h2>
            </div>
            <div class="stack-list">
              <div v-for="item in confirmations" :key="item.id" class="stack-item">
                <div class="stack-item-main">
                  <span class="mono">{{ item.task_no }}</span>
                  <strong>{{ item.item_type }} — {{ item.item_name }}</strong>
                </div>
                <span :class="['status-badge', confirmationStatusClass(item.status)]">{{ t(`confirmations.status.${item.status}`) }}</span>
              </div>
              <div v-if="confirmations.length === 0" class="empty-state">
                <p>{{ t('common.noData') }}</p>
              </div>
            </div>
          </article>

          <article class="dashboard-card detail-card">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.files') }}</h2>
            </div>
            <div class="stack-list">
              <div v-for="item in files" :key="item.id" class="stack-item">
                <span class="mono">{{ item.file_name }}</span>
                <p>{{ item.file_type }} / {{ item.version }} / {{ item.size }}</p>
                <p class="file-visibility">{{ fileVisibilityLabel(item.visibility) }}</p>
              </div>
              <div v-if="files.length === 0" class="empty-state">
                <p>{{ t('common.noData') }}</p>
              </div>
            </div>
          </article>

          <article class="dashboard-card detail-card">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.logistics') }}</h2>
            </div>
            <div class="stack-list">
              <div v-for="item in logistics" :key="item.id" class="stack-item">
                <div class="stack-item-main">
                  <strong>{{ item.company }}</strong>
                  <p class="mono">{{ item.tracking_no }}</p>
                </div>
                <div class="logistics-meta">
                  <span>{{ t('logistics.columns.etd') }}: {{ formatDate(item.etd) }}</span>
                  <span>{{ t('logistics.columns.eta') }}: {{ formatDate(item.eta) }}</span>
                </div>
                <span class="status-badge" :class="`status-${item.status}`">{{ logisticsStatusLabel(item.status) }}</span>
                <p v-if="item.latest_note" class="logistics-note">{{ item.latest_note }}</p>
              </div>
              <div v-if="logistics.length === 0" class="empty-state">
                <p>{{ t('common.noData') }}</p>
              </div>
            </div>
          </article>

          <article class="dashboard-card detail-card detail-span-2">
            <div class="card-head">
              <h2>{{ t('orderDetail.sections.messages') }}</h2>
            </div>
            <div class="stack-list">
              <div v-for="thread in threads" :key="thread.id" class="stack-item">
                <strong>{{ thread.title }}</strong>
                <p>{{ t('messageCenter.threadCreatedAt') }}: {{ formatDate(thread.created_at) }}</p>
              </div>
              <div v-if="threads.length === 0" class="empty-state">
                <p>{{ t('common.noData') }}</p>
              </div>
            </div>
          </article>
        </section>
      </template>

      <div v-else class="empty-state">
        <p>{{ t('common.noData') }}</p>
      </div>
    </section>
  </main>
</template>