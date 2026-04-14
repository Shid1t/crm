<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { createMessageRecord, fetchMessageRecords, fetchMessageThreads } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

interface Conversation {
  id: string
  customerName: string
  orderNo: string
  lastMessage: string
  lastTime: string
  unread: number
}

interface ChatMessage {
  id: string
  sender: 'admin' | 'customer'
  content: string
  time: string
}

const { t } = useI18n()

const keyword = ref('')
const activeConversationId = ref('')
const draft = ref('')

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

const conversations = ref<Conversation[]>([])

const threadMap: Record<string, ChatMessage[]> = {}

onMounted(async () => {
  try {
    const data = await fetchMessageThreads()
    conversations.value = data.map((item) => {
      const id = String(item.id)
      threadMap[id] = []
      return {
        id,
        customerName: item.customer_name || '-',
        orderNo: item.order_no || '-',
        lastMessage: item.title,
        lastTime: new Date(item.created_at).toLocaleString(),
        unread: 0,
      }
    })
    activeConversationId.value = conversations.value[0]?.id || ''
  } catch {
    conversations.value = []
    activeConversationId.value = ''
  }
})

watch(activeConversationId, async (nextId) => {
  if (!nextId) {
    return
  }
  try {
    const records = await fetchMessageRecords(Number(nextId))
    threadMap[nextId] = records.map((item) => ({
      id: String(item.id),
      sender: item.sender_role === 'admin' ? 'admin' : 'customer',
      content: item.content,
      time: new Date(item.created_at).toLocaleString(),
    }))
  } catch {
    threadMap[nextId] = []
  }
})

const filteredConversations = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return conversations.value.filter((item) => {
    if (!q) return true
    const text = `${item.customerName} ${item.orderNo} ${item.lastMessage}`.toLowerCase()
    return text.includes(q)
  })
})

const activeConversation = computed(
  () => conversations.value.find((item) => item.id === activeConversationId.value) || conversations.value[0],
)

const activeMessages = computed(() => {
  const activeId = activeConversation.value?.id
  return activeId ? threadMap[activeId] || [] : []
})

async function sendMessage() {
  if (!draft.value.trim()) {
    return
  }

  const activeId = activeConversation.value?.id
  if (!activeId) {
    return
  }

  try {
    const created = await createMessageRecord(Number(activeId), draft.value.trim())
    threadMap[activeId] = [
      ...(threadMap[activeId] || []),
      {
        id: String(created.id),
        sender: created.sender_role === 'admin' ? 'admin' : 'customer',
        content: created.content,
        time: new Date(created.created_at).toLocaleString(),
      },
    ]
    draft.value = ''
  } catch {
    return
  }
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'messages' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('messageCenter.kicker') }}</p>
          <h1>{{ t('messageCenter.title') }}</h1>
          <p>{{ t('messageCenter.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('messageCenter.actions.markAllRead') }}</button>
          <button class="primary-button">{{ t('messageCenter.actions.newThread') }}</button>
        </div>
      </header>

      <section class="message-layout dashboard-card">
        <aside class="conversation-list">
          <input v-model.trim="keyword" class="dashboard-search" :placeholder="t('messageCenter.searchPlaceholder')" type="text" />

          <div class="conversation-items">
            <button
              v-for="item in filteredConversations"
              :key="item.id"
              class="conversation-item"
              :class="{ active: item.id === activeConversationId }"
              type="button"
              @click="activeConversationId = item.id"
            >
              <div class="conversation-top">
                <strong>{{ item.customerName }}</strong>
                <span>{{ item.lastTime }}</span>
              </div>
              <p class="mono">{{ item.orderNo }}</p>
              <p>{{ item.lastMessage }}</p>
              <span v-if="item.unread" class="unread-badge">{{ item.unread }}</span>
            </button>
          </div>
        </aside>

        <section class="message-thread">
          <header class="thread-header">
            <h2>{{ activeConversation?.customerName }}</h2>
            <p>{{ t('messageCenter.orderTag') }}: {{ activeConversation?.orderNo }}</p>
          </header>

          <div class="thread-messages">
            <article v-for="msg in activeMessages" :key="msg.id" class="chat-bubble" :class="msg.sender">
              <strong>{{ msg.sender === 'admin' ? t('messageCenter.sender.admin') : t('messageCenter.sender.customer') }}</strong>
              <p>{{ msg.content }}</p>
              <span>{{ msg.time }}</span>
            </article>
          </div>

          <footer class="thread-input">
            <textarea v-model="draft" :placeholder="t('messageCenter.inputPlaceholder')" rows="3" />
            <button class="primary-button" type="button" @click="sendMessage">{{ t('messageCenter.actions.send') }}</button>
          </footer>
        </section>
      </section>
    </section>
  </main>
</template>
