<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

import LocaleSwitch from '../components/LocaleSwitch.vue'
import {
  createLogistics,
  createMessageRecord,
  createMessageThread,
  createOrderItem,
  deleteFileRecord,
  deleteLogistics,
  deleteOrderItem,
  fetchFiles,
  fetchLogistics,
  fetchMessageRecords,
  fetchMessageThreads,
  fetchOrderItems,
  fetchOrders,
  updateLogistics,
  updateOrder,
  updateOrderItem,
  uploadOrderFile,
} from '../api/resources'
import type { FileDTO, LogisticsDTO, MessageRecordDTO, MessageThreadDTO, OrderDTO, OrderItemDTO } from '../api/resources'

type OrderStatus = 'pending' | 'pending_payment' | 'paid' | 'pending_shipment' | 'shipped' | 'completed'

const route = useRoute()
const { t } = useI18n()

const orderNo = computed(() => String(route.params.orderNo || ''))
const order = ref<OrderDTO | null>(null)
const items = ref<OrderItemDTO[]>([])
const files = ref<FileDTO[]>([])
const logistics = ref<LogisticsDTO[]>([])
const threads = ref<MessageThreadDTO[]>([])
const messages = ref<MessageRecordDTO[]>([])
const activeThreadId = ref<number | null>(null)
const loading = ref(true)
const savingStatus = ref(false)
const error = ref('')

const statusDraft = ref<OrderStatus>('pending')
const replyDraftMap = reactive<Record<number, string>>({})
const replyOpenMap = reactive<Record<number, boolean>>({})
const newMessage = ref('')

const showUploadDialog = ref(false)
const showLogisticsDialog = ref(false)
const showItemDialog = ref(false)
const editingItemId = ref<number | null>(null)

const uploadFile = ref<File | null>(null)
const uploadForm = reactive({
  file_type: 'PI',
  version: 'v1',
  visibility: 'customer' as 'customer' | 'internal',
})

const logisticsForm = reactive({
  id: 0,
  company: '',
  tracking_no: '',
  etd: '',
  eta: '',
  status: 'preparing' as LogisticsDTO['status'],
  latest_note: '',
})

const itemForm = reactive({
  sku: '',
  name: '',
  spec: '',
  qty: 1,
  unit_price: '0',
})

const statusOptions = computed(() => [
  { value: 'pending', label: t('order.status.pending') },
  { value: 'pending_payment', label: t('order.status.pending_payment') },
  { value: 'paid', label: t('order.status.paid') },
  { value: 'pending_shipment', label: t('order.status.pending_shipment') },
  { value: 'shipped', label: t('order.status.shipped') },
  { value: 'completed', label: t('order.status.completed') },
])

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
    { key: t('order.columns.description'), value: order.value.description || '-' },
    { key: t('orderDetail.basic.currency'), value: order.value.currency },
    { key: t('orderDetail.basic.amount'), value: Number(order.value.amount).toLocaleString() },
    { key: t('orderDetail.basic.eta'), value: order.value.eta || '-' },
  ]
})

async function loadOrderBundle() {
  loading.value = true
  error.value = ''
  try {
    const [orderRes, itemsRes, fileRes, logRes, threadRes] = await Promise.all([
      fetchOrders({ order_no: orderNo.value }),
      fetchOrderItems({ order_no: orderNo.value }),
      fetchFiles({ order_no: orderNo.value }),
      fetchLogistics({ order_no: orderNo.value }),
      fetchMessageThreads({ order_no: orderNo.value }),
    ])
    order.value = orderRes[0] || null
    items.value = itemsRes
    files.value = fileRes
    logistics.value = logRes
    threads.value = threadRes
    statusDraft.value = (order.value?.status || 'pending') as OrderStatus

    if (threads.value.length > 0) {
      if (!activeThreadId.value || !threads.value.some((x) => x.id === activeThreadId.value)) {
        activeThreadId.value = threads.value[0].id
      }
      await loadMessages(activeThreadId.value)
    } else {
      activeThreadId.value = null
      messages.value = []
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function loadMessages(threadId: number | null) {
  if (!threadId) {
    messages.value = []
    return
  }
  messages.value = await fetchMessageRecords(threadId)
}

onMounted(loadOrderBundle)
watch(orderNo, loadOrderBundle)
watch(activeThreadId, loadMessages)

async function saveStatus() {
  if (!order.value) return
  savingStatus.value = true
  try {
    await updateOrder(order.value.id, { status: statusDraft.value })
    await loadOrderBundle()
  } finally {
    savingStatus.value = false
  }
}

function openNewItem() {
  editingItemId.value = null
  itemForm.sku = ''
  itemForm.name = ''
  itemForm.spec = ''
  itemForm.qty = 1
  itemForm.unit_price = '0'
  showItemDialog.value = true
}

function openEditItem(item: OrderItemDTO) {
  editingItemId.value = item.id
  itemForm.sku = item.sku
  itemForm.name = item.name
  itemForm.spec = item.spec
  itemForm.qty = item.qty
  itemForm.unit_price = item.unit_price
  showItemDialog.value = true
}

async function saveItem() {
  if (!order.value || !itemForm.name.trim()) return
  if (editingItemId.value) {
    await updateOrderItem(editingItemId.value, {
      sku: itemForm.sku,
      name: itemForm.name,
      spec: itemForm.spec,
      qty: itemForm.qty,
      unit_price: itemForm.unit_price,
      order: order.value.id,
    })
  } else {
    await createOrderItem({
      order: order.value.id,
      sku: itemForm.sku,
      name: itemForm.name,
      spec: itemForm.spec,
      qty: itemForm.qty,
      unit_price: itemForm.unit_price,
    })
  }
  showItemDialog.value = false
  await loadOrderBundle()
}

async function removeItem(item: OrderItemDTO) {
  if (!window.confirm(`删除商品 ${item.name} ?`)) return
  await deleteOrderItem(item.id)
  await loadOrderBundle()
}

function pickUploadFile(event: Event) {
  const target = event.target as HTMLInputElement
  uploadFile.value = target.files?.[0] || null
}

async function submitUploadFile() {
  if (!order.value || !uploadFile.value) return
  await uploadOrderFile({
    order: order.value.id,
    file: uploadFile.value,
    file_type: uploadForm.file_type,
    version: uploadForm.version,
    visibility: uploadForm.visibility,
  })
  showUploadDialog.value = false
  uploadFile.value = null
  await loadOrderBundle()
}

async function removeFile(file: FileDTO) {
  if (!window.confirm(`删除文件 ${file.file_name} ?`)) return
  await deleteFileRecord(file.id)
  await loadOrderBundle()
}

function openNewLogistics() {
  logisticsForm.id = 0
  logisticsForm.company = ''
  logisticsForm.tracking_no = ''
  logisticsForm.etd = ''
  logisticsForm.eta = ''
  logisticsForm.status = 'preparing'
  logisticsForm.latest_note = ''
  showLogisticsDialog.value = true
}

function openEditLogistics(item: LogisticsDTO) {
  logisticsForm.id = item.id
  logisticsForm.company = item.company
  logisticsForm.tracking_no = item.tracking_no
  logisticsForm.etd = item.etd || ''
  logisticsForm.eta = item.eta || ''
  logisticsForm.status = item.status
  logisticsForm.latest_note = item.latest_note || ''
  showLogisticsDialog.value = true
}

async function saveLogistics() {
  if (!order.value || !logisticsForm.tracking_no.trim()) return
  if (logisticsForm.id) {
    await updateLogistics(logisticsForm.id, {
      order: order.value.id,
      company: logisticsForm.company,
      tracking_no: logisticsForm.tracking_no,
      etd: logisticsForm.etd || null,
      eta: logisticsForm.eta || null,
      status: logisticsForm.status,
      latest_note: logisticsForm.latest_note,
    })
  } else {
    await createLogistics({
      order: order.value.id,
      company: logisticsForm.company,
      tracking_no: logisticsForm.tracking_no,
      etd: logisticsForm.etd || null,
      eta: logisticsForm.eta || null,
      status: logisticsForm.status,
      latest_note: logisticsForm.latest_note,
    })
  }
  showLogisticsDialog.value = false
  await loadOrderBundle()
}

async function removeLogistics(item: LogisticsDTO) {
  if (!window.confirm(`删除物流轨迹 ${item.tracking_no} ?`)) return
  await deleteLogistics(item.id)
  await loadOrderBundle()
}

async function createThread() {
  if (!order.value) return
  const title = window.prompt('请输入会话主题', `${order.value.order_no} 订单沟通`) || ''
  if (!title.trim()) return
  const created = await createMessageThread({ customer: order.value.customer, order: order.value.id, title })
  activeThreadId.value = created.id
  await loadOrderBundle()
}

async function sendMessage(parentId?: number) {
  const content = (parentId ? replyDraftMap[parentId] || '' : newMessage.value).trim()
  if (!content || !activeThreadId.value) return
  await createMessageRecord(activeThreadId.value, content, parentId)
  if (parentId) {
    replyDraftMap[parentId] = ''
    replyOpenMap[parentId] = false
  } else {
    newMessage.value = ''
  }
  await loadMessages(activeThreadId.value)
}

function toggleReply(messageId: number) {
  replyOpenMap[messageId] = !replyOpenMap[messageId]
  if (!replyDraftMap[messageId]) replyDraftMap[messageId] = ''
}

const rootMessages = computed(() => messages.value.filter((m) => !m.parent))
const repliesByParent = computed(() => {
  const map: Record<number, MessageRecordDTO[]> = {}
  for (const msg of messages.value) {
    if (!msg.parent) continue
    if (!map[msg.parent]) map[msg.parent] = []
    map[msg.parent].push(msg)
  }
  return map
})

const formatDate = (d: string | null) => (d ? new Date(d).toLocaleString() : '-')
const fileVisibilityLabel = (v: string) => (v === 'customer' ? t('orderDetail.visibility.customer') : t('orderDetail.visibility.internal'))
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'orders' }" :to="item.to">{{ item.label }}</RouterLink>
          <button v-else class="nav-item" type="button">{{ item.label }}</button>
        </template>
      </nav>
      <div class="sidebar-footer"><LocaleSwitch /></div>
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
        </div>
      </header>

      <div v-if="loading" class="loading-state"><div class="spinner" /><p>{{ t('common.loading') }}</p></div>
      <div v-else-if="error" class="error-state"><p>{{ error }}</p><button class="primary-button" @click="loadOrderBundle">{{ t('common.retry') }}</button></div>

      <template v-else-if="order">
        <section class="detail-grid">
          <article class="dashboard-card detail-card">
            <div class="card-head"><h2>{{ t('orderDetail.sections.basic') }}</h2></div>
            <div class="kv-grid"><div v-for="row in basicInfo" :key="row.key" class="kv-row"><span>{{ row.key }}</span><strong>{{ row.value }}</strong></div></div>
            <div class="status-editor">
              <label class="field">
                <span>{{ t('orderDetail.basic.status') }}</span>
                <select v-model="statusDraft" class="customer-select">
                  <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </label>
              <button class="primary-button" :disabled="savingStatus" @click="saveStatus">{{ t('order.actions.save') }}</button>
            </div>
          </article>

          <article class="dashboard-card detail-card detail-span-2">
            <div class="card-head"><h2>{{ t('orderDetail.sections.items') }}</h2><button class="primary-button" @click="openNewItem">新增商品</button></div>
            <table class="customer-table">
              <thead><tr><th>SKU</th><th>{{ t('orderDetail.columns.name') }}</th><th>{{ t('orderDetail.columns.spec') }}</th><th>{{ t('orderDetail.columns.qty') }}</th><th>{{ t('orderDetail.columns.unit') }}</th><th>{{ t('orderDetail.columns.total') }}</th><th>{{ t('order.columns.actions') }}</th></tr></thead>
              <tbody>
                <tr v-for="it in items" :key="it.id">
                  <td class="mono">{{ it.sku }}</td>
                  <td>{{ it.name }}</td>
                  <td>{{ it.spec }}</td>
                  <td>{{ it.qty }}</td>
                  <td>{{ order.currency }} {{ it.unit_price }}</td>
                  <td>{{ it.total }}</td>
                  <td>
                    <div class="table-actions">
                      <button class="text-button" @click="openEditItem(it)">{{ t('order.actions.edit') }}</button>
                      <button class="text-button" @click="removeItem(it)">{{ t('order.actions.delete') }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </article>

          <article class="dashboard-card detail-card detail-span-2 compact-card">
            <div class="card-head"><h2>{{ t('orderDetail.sections.files') }}</h2><button class="primary-button" @click="showUploadDialog = true">上传文件</button></div>
            <table class="customer-table">
              <thead><tr><th>File</th><th>Type</th><th>Version</th><th>Size</th><th>Visibility</th><th>{{ t('order.columns.actions') }}</th></tr></thead>
              <tbody>
                <tr v-for="f in files" :key="f.id">
                  <td class="mono"><a v-if="f.file_url" :href="f.file_url" target="_blank">{{ f.file_name }}</a><span v-else>{{ f.file_name }}</span></td>
                  <td>{{ f.file_type }}</td>
                  <td>{{ f.version }}</td>
                  <td>{{ f.size }}</td>
                  <td>{{ fileVisibilityLabel(f.visibility) }}</td>
                  <td><button class="text-button" @click="removeFile(f)">{{ t('order.actions.delete') }}</button></td>
                </tr>
              </tbody>
            </table>
          </article>

          <article class="dashboard-card detail-card detail-span-2 compact-card">
            <div class="card-head"><h2>{{ t('orderDetail.sections.logistics') }}</h2><button class="primary-button" @click="openNewLogistics">新增物流</button></div>
            <table class="customer-table">
              <thead><tr><th>Company</th><th>Tracking No.</th><th>ETD</th><th>ETA</th><th>Status</th><th>Latest Note</th><th>{{ t('order.columns.actions') }}</th></tr></thead>
              <tbody>
                <tr v-for="l in logistics" :key="l.id">
                  <td>{{ l.company }}</td>
                  <td class="mono">{{ l.tracking_no }}</td>
                  <td>{{ l.etd || '-' }}</td>
                  <td>{{ l.eta || '-' }}</td>
                  <td>{{ l.status }}</td>
                  <td>{{ l.latest_note }}</td>
                  <td>
                    <div class="table-actions">
                      <button class="text-button" @click="openEditLogistics(l)">{{ t('order.actions.edit') }}</button>
                      <button class="text-button" @click="removeLogistics(l)">{{ t('order.actions.delete') }}</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </article>

          <article class="dashboard-card detail-card detail-span-2 compact-card">
            <div class="card-head"><h2>{{ t('orderDetail.sections.messages') }}</h2><button class="primary-button" @click="createThread">新建会话</button></div>
            <div class="message-layout-local">
              <aside class="message-thread-list">
                <button v-for="th in threads" :key="th.id" class="conversation-item" :class="{ active: activeThreadId === th.id }" @click="activeThreadId = th.id">
                  <strong>{{ th.title }}</strong>
                  <p class="mono">{{ th.order_no }}</p>
                </button>
              </aside>
              <section class="message-thread-view">
                <div class="thread-messages local-thread">
                  <article v-for="m in rootMessages" :key="m.id" class="chat-bubble" :class="m.sender_role === 'admin' ? 'admin' : 'customer'">
                    <strong>{{ m.sender_role === 'admin' ? 'Admin' : 'Customer' }}</strong>
                    <p>{{ m.content }}</p>
                    <span>{{ formatDate(m.created_at) }}</span>

                    <div v-if="repliesByParent[m.id]?.length" class="reply-list">
                      <article v-for="r in repliesByParent[m.id]" :key="r.id" class="chat-bubble reply" :class="r.sender_role === 'admin' ? 'admin' : 'customer'">
                        <strong>{{ r.sender_role === 'admin' ? 'Admin' : 'Customer' }}</strong>
                        <p>{{ r.content }}</p>
                        <span>{{ formatDate(r.created_at) }}</span>
                      </article>
                    </div>

                    <div class="reply-action-row">
                      <button class="text-button" @click="toggleReply(m.id)">回复该条</button>
                    </div>
                    <div v-if="replyOpenMap[m.id]" class="reply-editor">
                      <textarea v-model="replyDraftMap[m.id]" rows="2" placeholder="输入回复内容" />
                      <button class="primary-button" @click="sendMessage(m.id)">发送回复</button>
                    </div>
                  </article>
                </div>

                <footer class="thread-input">
                  <textarea v-model="newMessage" rows="3" placeholder="输入新消息" />
                  <button class="primary-button" @click="sendMessage()">发送消息</button>
                </footer>
              </section>
            </div>
          </article>
        </section>
      </template>

      <div v-else class="empty-state"><p>{{ t('common.noData') }}</p></div>
    </section>

    <Teleport to="body">
      <div v-if="showUploadDialog" class="modal-overlay" @click.self="showUploadDialog = false">
        <section class="modal-panel order-form-modal" role="dialog" aria-modal="true">
          <div class="card-head modal-head"><h2>上传订单文件</h2><button class="text-button modal-close" @click="showUploadDialog = false">关闭</button></div>
          <div class="account-form-grid">
            <label class="field"><span>文件</span><input type="file" @change="pickUploadFile" /></label>
            <label class="field"><span>文件类型</span><input v-model="uploadForm.file_type" type="text" placeholder="PI/CI/PL/BL..." /></label>
            <label class="field"><span>版本</span><input v-model="uploadForm.version" type="text" placeholder="v1" /></label>
            <label class="field"><span>可见性</span><select v-model="uploadForm.visibility" class="customer-select"><option value="customer">customer</option><option value="internal">internal</option></select></label>
          </div>
          <div class="header-actions modal-actions"><button class="secondary-button" @click="showUploadDialog = false">取消</button><button class="primary-button" @click="submitUploadFile">上传</button></div>
        </section>
      </div>

      <div v-if="showLogisticsDialog" class="modal-overlay" @click.self="showLogisticsDialog = false">
        <section class="modal-panel order-form-modal" role="dialog" aria-modal="true">
          <div class="card-head modal-head"><h2>{{ logisticsForm.id ? '编辑物流轨迹' : '新增物流轨迹' }}</h2><button class="text-button modal-close" @click="showLogisticsDialog = false">关闭</button></div>
          <div class="account-form-grid">
            <label class="field"><span>物流公司</span><input v-model="logisticsForm.company" type="text" placeholder="Maersk" /></label>
            <label class="field"><span>追踪单号</span><input v-model="logisticsForm.tracking_no" type="text" placeholder="MSKU1234567" /></label>
            <label class="field"><span>ETD</span><input v-model="logisticsForm.etd" type="date" /></label>
            <label class="field"><span>ETA</span><input v-model="logisticsForm.eta" type="date" /></label>
            <label class="field"><span>状态</span><select v-model="logisticsForm.status" class="customer-select"><option value="preparing">preparing</option><option value="inTransit">inTransit</option><option value="customs">customs</option><option value="delayed">delayed</option><option value="delivered">delivered</option></select></label>
            <label class="field field-span-2"><span>最新节点</span><textarea v-model="logisticsForm.latest_note" rows="3" placeholder="填写最新运输节点信息" /></label>
          </div>
          <div class="header-actions modal-actions"><button class="secondary-button" @click="showLogisticsDialog = false">取消</button><button class="primary-button" @click="saveLogistics">保存</button></div>
        </section>
      </div>

      <div v-if="showItemDialog" class="modal-overlay" @click.self="showItemDialog = false">
        <section class="modal-panel order-form-modal" role="dialog" aria-modal="true">
          <div class="card-head modal-head"><h2>{{ editingItemId ? '编辑商品' : '新增商品' }}</h2><button class="text-button modal-close" @click="showItemDialog = false">关闭</button></div>
          <div class="account-form-grid">
            <label class="field"><span>SKU</span><input v-model="itemForm.sku" type="text" /></label>
            <label class="field"><span>产品名称</span><input v-model="itemForm.name" type="text" /></label>
            <label class="field field-span-2"><span>规格描述</span><textarea v-model="itemForm.spec" rows="2" /></label>
            <label class="field"><span>数量</span><input v-model.number="itemForm.qty" type="number" min="1" /></label>
            <label class="field"><span>单价</span><input v-model="itemForm.unit_price" type="number" min="0" step="0.01" /></label>
          </div>
          <div class="header-actions modal-actions"><button class="secondary-button" @click="showItemDialog = false">取消</button><button class="primary-button" @click="saveItem">保存</button></div>
        </section>
      </div>
    </Teleport>
  </main>
</template>
