<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { createOrder, deleteOrder, fetchConfirmations, fetchCustomers, fetchOrders, updateOrder } from '../api/resources'
import type { CustomerDTO, OrderDTO } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

type OrderStatus = 'pending' | 'confirmed' | 'production' | 'shipped' | 'completed' | 'exception'

interface OrderRow {
  id: number
  customer: number
  orderNo: string
  customerName: string
  orderDate: string
  amount: string
  currency: string
  eta: string
  status: OrderStatus
  confirmationRate: string
}

const { t } = useI18n()

const search = ref('')
const statusFilter = ref<'all' | OrderStatus>('all')
const orders = ref<OrderRow[]>([])
const customers = ref<CustomerDTO[]>([])
const loading = ref(false)
const errorMessage = ref('')

const showForm = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const showCloseConfirm = ref(false)
const deleteCandidate = ref<OrderRow | null>(null)
const initialFormSignature = ref('')
const pageSize = ref(10)
const currentPage = ref(1)
const pageSizeOptions = [10, 20, 50]
const form = ref({
  order_no: '',
  customer: '',
  order_date: '',
  amount: '',
  currency: 'USD',
  eta: '',
  status: 'pending' as OrderStatus,
})

async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [orderRows, confirmationRows, customerRows] = await Promise.all([
      fetchOrders(),
      fetchConfirmations(),
      fetchCustomers(),
    ])
    customers.value = customerRows
    const confirmCountMap = confirmationRows.reduce<Record<string, { done: number; total: number }>>((acc, item) => {
      const key = item.order_no || ''
      if (!key) return acc
      if (!acc[key]) acc[key] = { done: 0, total: 0 }
      acc[key].total += 1
      if (item.status === 'approved') acc[key].done += 1
      return acc
    }, {})

    orders.value = orderRows.map((item) => {
      const progress = confirmCountMap[item.order_no]
      const ratio = progress ? `${Math.round((progress.done / Math.max(progress.total, 1)) * 100)}%` : '0%'
      return {
        id: item.id,
        customer: item.customer,
        orderNo: item.order_no,
        customerName: item.customer_name || '-',
        orderDate: item.order_date,
        amount: item.amount,
        currency: item.currency,
        eta: item.eta || '-',
        status: item.status,
        confirmationRate: ratio,
      }
    })
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
    orders.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

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
  { value: 'all', label: t('order.filters.all') },
  { value: 'pending', label: t('order.status.pending') },
  { value: 'confirmed', label: t('order.status.confirmed') },
  { value: 'production', label: t('order.status.production') },
  { value: 'shipped', label: t('order.status.shipped') },
  { value: 'completed', label: t('order.status.completed') },
  { value: 'exception', label: t('order.status.exception') },
])

const filteredOrders = computed(() => {
  const keyword = search.value.toLowerCase().trim()
  return orders.value.filter((item) => {
    const matchStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    const haystack = `${item.orderNo} ${item.customerName} ${item.amount}`.toLowerCase()
    const matchKeyword = !keyword || haystack.includes(keyword)
    return matchStatus && matchKeyword
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredOrders.value.length / pageSize.value)))

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredOrders.value.slice(start, start + pageSize.value)
})

const pageStart = computed(() => {
  if (!filteredOrders.value.length) return 0
  return (currentPage.value - 1) * pageSize.value + 1
})

const pageEnd = computed(() => {
  if (!filteredOrders.value.length) return 0
  return Math.min(currentPage.value * pageSize.value, filteredOrders.value.length)
})

const pageNumbers = computed(() => {
  const total = totalPages.value
  if (total <= 7) return Array.from({ length: total }, (_, idx) => idx + 1)
  if (currentPage.value <= 4) return [1, 2, 3, 4, 5, 6, total]
  if (currentPage.value >= total - 3) return [1, total - 5, total - 4, total - 3, total - 2, total - 1, total]
  return [1, currentPage.value - 2, currentPage.value - 1, currentPage.value, currentPage.value + 1, currentPage.value + 2, total]
})

watch([search, statusFilter, pageSize], () => {
  currentPage.value = 1
})

watch(filteredOrders, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
})

function formSignature() {
  return JSON.stringify(form.value)
}

function markFormPristine() {
  initialFormSignature.value = formSignature()
}

function hasUnsavedChanges() {
  return formSignature() !== initialFormSignature.value
}

function statusLabel(status: OrderStatus) {
  return t(`order.status.${status}`)
}

function openCreate() {
  editingId.value = null
  form.value = {
    order_no: '',
    customer: String(customers.value[0]?.id || ''),
    order_date: '',
    amount: '',
    currency: 'USD',
    eta: '',
    status: 'pending',
  }
  showForm.value = true
  showCloseConfirm.value = false
  markFormPristine()
}

function openEdit(row: OrderRow) {
  editingId.value = row.id
  form.value = {
    order_no: row.orderNo,
    customer: String(row.customer),
    order_date: row.orderDate,
    amount: row.amount,
    currency: row.currency,
    eta: row.eta === '-' ? '' : row.eta,
    status: row.status,
  }
  showForm.value = true
  showCloseConfirm.value = false
  markFormPristine()
}

function closeForm() {
  showForm.value = false
  showCloseConfirm.value = false
}

function requestCloseForm() {
  if (submitting.value) return
  if (hasUnsavedChanges()) {
    showCloseConfirm.value = true
    return
  }
  closeForm()
}

function continueEditing() {
  showCloseConfirm.value = false
}

function discardAndClose() {
  closeForm()
}

async function saveAndClose() {
  showCloseConfirm.value = false
  await submitForm()
}

function goToPage(page: number) {
  currentPage.value = Math.min(totalPages.value, Math.max(1, page))
}

function requestDelete(row: OrderRow) {
  deleteCandidate.value = row
}

function cancelDelete() {
  deleteCandidate.value = null
}

async function confirmDelete() {
  const row = deleteCandidate.value
  if (!row) return
  deleteCandidate.value = null
  try {
    await deleteOrder(row.id)
    await loadData()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  }
}

async function submitForm() {
  if (!form.value.order_no || !form.value.customer || !form.value.order_date || !form.value.amount) {
    errorMessage.value = t('order.form.required')
    return
  }

  submitting.value = true
  errorMessage.value = ''
  const payload: Omit<OrderDTO, 'id' | 'customer_name'> = {
    order_no: form.value.order_no,
    customer: Number(form.value.customer),
    order_date: form.value.order_date,
    amount: form.value.amount,
    currency: form.value.currency,
    eta: form.value.eta || null,
    status: form.value.status,
  }
  try {
    if (editingId.value) {
      await updateOrder(editingId.value, payload)
    } else {
      await createOrder(payload)
    }
    closeForm()
    await loadData()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  } finally {
    submitting.value = false
  }
}

async function removeOrder(row: OrderRow) {
  requestDelete(row)
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
          <p class="panel-kicker">{{ t('order.kicker') }}</p>
          <h1>{{ t('order.title') }}</h1>
          <p>{{ t('order.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button" @click="loadData">{{ t('common.retry') }}</button>
          <button class="primary-button" @click="openCreate">{{ t('order.actions.create') }}</button>
        </div>
      </header>

      <section class="dashboard-card customer-filter-bar">
        <input v-model.trim="search" class="dashboard-search" :placeholder="t('order.filters.keywordPlaceholder')" type="text" />

        <select v-model="statusFilter" class="customer-select">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>

        <div class="customer-count">
          <strong>{{ filteredOrders.length }}</strong>
          <span>{{ t('order.filters.resultCount') }}</span>
        </div>
      </section>

      <section class="dashboard-card customer-table-wrap">
        <table class="customer-table">
          <thead>
            <tr>
              <th>{{ t('order.columns.orderNo') }}</th>
              <th>{{ t('order.columns.customerName') }}</th>
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
            <tr v-for="item in paginatedOrders" :key="item.id">
              <td class="mono">{{ item.orderNo }}</td>
              <td>{{ item.customerName }}</td>
              <td>{{ item.orderDate }}</td>
              <td>{{ item.amount }}</td>
              <td>{{ item.currency }}</td>
              <td>{{ item.eta }}</td>
              <td>{{ item.confirmationRate }}</td>
              <td>
                <span class="status-tag" :class="`order-${item.status}`">{{ statusLabel(item.status) }}</span>
              </td>
              <td>
                <div class="table-actions">
                  <RouterLink class="text-button" :to="`/admin/orders/${item.orderNo}`">{{ t('order.actions.view') }}</RouterLink>
                  <button class="text-button" type="button" @click="openEdit(item)">{{ t('order.actions.edit') }}</button>
                  <button class="text-button" type="button" @click="removeOrder(item)">{{ t('order.actions.delete') }}</button>
                </div>
              </td>
            </tr>
            <tr v-if="!paginatedOrders.length">
              <td colspan="9">{{ t('common.noData') }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="filteredOrders.length" class="table-pagination">
          <p>
            {{ t('order.pagination.summary', { start: pageStart, end: pageEnd, total: filteredOrders.length }) }}
          </p>

          <div class="pagination-controls">
            <label class="pagination-size">
              <span>{{ t('order.pagination.pageSize') }}</span>
              <select v-model.number="pageSize" class="customer-select pagination-select">
                <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
              </select>
            </label>

            <button
              class="secondary-button pagination-button"
              type="button"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              {{ t('order.pagination.prev') }}
            </button>

            <button
              v-for="page in pageNumbers"
              :key="page"
              class="secondary-button pagination-button"
              :class="{ active: currentPage === page }"
              type="button"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>

            <button
              class="secondary-button pagination-button"
              type="button"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              {{ t('order.pagination.next') }}
            </button>
          </div>
        </div>
      </section>

      <p v-if="errorMessage" class="form-feedback visible">{{ errorMessage }}</p>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <p>{{ t('common.loading') }}</p>
      </div>
    </section>

    <Teleport to="body">
      <div v-if="showForm" class="modal-overlay" @click.self="requestCloseForm">
        <section class="modal-panel order-form-modal" role="dialog" aria-modal="true">
          <div class="card-head modal-head">
            <h2>{{ editingId ? t('order.actions.edit') : t('order.actions.create') }}</h2>
            <button class="text-button modal-close" type="button" @click="requestCloseForm">{{ t('order.dialogs.close') }}</button>
          </div>

          <div class="account-form-grid">
            <label class="field">
              <span>{{ t('order.columns.orderNo') }}</span>
              <input v-model.trim="form.order_no" type="text" />
            </label>
            <label class="field">
              <span>{{ t('order.columns.customerName') }}</span>
              <select v-model="form.customer" class="customer-select">
                <option v-for="c in customers" :key="c.id" :value="String(c.id)">{{ c.company_name }}</option>
              </select>
            </label>
            <label class="field">
              <span>{{ t('order.columns.orderDate') }}</span>
              <input v-model="form.order_date" type="date" />
            </label>
            <label class="field">
              <span>{{ t('order.columns.amount') }}</span>
              <input v-model="form.amount" type="number" min="0" step="0.01" />
            </label>
            <label class="field">
              <span>{{ t('order.columns.currency') }}</span>
              <input v-model.trim="form.currency" type="text" />
            </label>
            <label class="field">
              <span>{{ t('order.columns.eta') }}</span>
              <input v-model="form.eta" type="date" />
            </label>
            <label class="field">
              <span>{{ t('order.columns.status') }}</span>
              <select v-model="form.status" class="customer-select">
                <option v-for="option in statusOptions.filter(i => i.value !== 'all')" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
          </div>

          <div class="header-actions modal-actions">
            <button class="secondary-button" type="button" @click="requestCloseForm">{{ t('order.actions.cancel') }}</button>
            <button class="primary-button" type="button" :disabled="submitting" @click="submitForm">{{ t('order.actions.save') }}</button>
          </div>
        </section>
      </div>

      <div v-if="showCloseConfirm" class="modal-overlay modal-overlay-confirm" @click.self="continueEditing">
        <section class="modal-panel confirm-modal" role="dialog" aria-modal="true">
          <h3>{{ t('order.dialogs.unsavedTitle') }}</h3>
          <p>{{ t('order.dialogs.unsavedDescription') }}</p>
          <div class="header-actions modal-actions">
            <button class="secondary-button" type="button" @click="continueEditing">{{ t('order.dialogs.continueEdit') }}</button>
            <button class="secondary-button danger-button" type="button" @click="discardAndClose">{{ t('order.dialogs.discard') }}</button>
            <button class="primary-button" type="button" :disabled="submitting" @click="saveAndClose">{{ t('order.dialogs.saveAndClose') }}</button>
          </div>
        </section>
      </div>

      <div v-if="deleteCandidate" class="modal-overlay modal-overlay-confirm" @click.self="cancelDelete">
        <section class="modal-panel confirm-modal" role="dialog" aria-modal="true">
          <h3>{{ t('order.dialogs.deleteTitle') }}</h3>
          <p>{{ t('order.dialogs.deleteDescription', { orderNo: deleteCandidate.orderNo }) }}</p>
          <div class="header-actions modal-actions">
            <button class="secondary-button" type="button" @click="cancelDelete">{{ t('order.actions.cancel') }}</button>
            <button class="secondary-button danger-button" type="button" @click="confirmDelete">{{ t('order.actions.delete') }}</button>
          </div>
        </section>
      </div>
    </Teleport>
  </main>
</template>
