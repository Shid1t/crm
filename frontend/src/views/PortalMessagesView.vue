<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { createMessageRecord, fetchMessageRecords, fetchMessageThreads } from '../api/resources'
import LocaleSwitch from '../components/LocaleSwitch.vue'

interface Conversation {
  id: string
  orderNo: string
  title: string
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
const activeId = ref('')
const draft = ref('')

const menuItems = computed(() => [
  { key: 'home', label: t('portal.menu.home'), to: '/portal/home' },
  { key: 'orders', label: t('portal.menu.orders'), to: '/portal/orders' },
  { key: 'confirmations', label: t('portal.menu.confirmations'), to: '/portal/confirmations' },
  { key: 'files', label: t('portal.menu.files'), to: '/portal/files' },
  { key: 'logistics', label: t('portal.menu.logistics'), to: '/portal/logistics' },
  { key: 'messages', label: t('portal.menu.messages'), to: '/portal/messages' },
  { key: 'account', label: t('portal.menu.account'), to: '/portal/account' },
])

const conversations = ref<Conversation[]>([])

const threads: Record<string, ChatMessage[]> = {}

onMounted(async () => {
  try {
    const data = await fetchMessageThreads()
    conversations.value = data.map((item) => {
      const id = String(item.id)
      threads[id] = []
      return {
        id,
        orderNo: item.order_no || '-',
        title: item.title,
        lastMessage: item.title,
        lastTime: new Date(item.created_at).toLocaleString(),
        unread: 0,
      }
    })
    activeId.value = conversations.value[0]?.id || ''
  } catch {
    conversations.value = []
    activeId.value = ''
  }
})

watch(activeId, async (nextId) => {
  if (!nextId) {
    return
  }
  try {
    const records = await fetchMessageRecords(Number(nextId))
    threads[nextId] = records.map((item) => ({
      id: String(item.id),
      sender: item.sender_role === 'admin' ? 'admin' : 'customer',
      content: item.content,
      time: new Date(item.created_at).toLocaleString(),
    }))
  } catch {
    threads[nextId] = []
  }
})

const filteredConversations = computed(() => {
  const q = keyword.value.toLowerCase().trim()
  return conversations.value.filter((item) => {
    if (!q) return true
    return `${item.orderNo} ${item.title} ${item.lastMessage}`.toLowerCase().includes(q)
  })
})

const activeConversation = computed(() => conversations.value.find((item) => item.id === activeId.value) || conversations.value[0])
const messages = computed(() => (activeConversation.value ? threads[activeConversation.value.id] || [] : []))

async function sendMessage() {
  if (!draft.value.trim() || !activeConversation.value) {
    return
  }

  try {
    const created = await createMessageRecord(Number(activeConversation.value.id), draft.value.trim())
    threads[activeConversation.value.id] = [
      ...messages.value,
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
          <p class="panel-kicker">{{ t('portalMessages.kicker') }}</p>
          <h1>{{ t('portalMessages.title') }}</h1>
          <p>{{ t('portalMessages.subtitle') }}</p>
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
              :class="{ active: item.id === activeId }"
              type="button"
              @click="activeId = item.id"
            >
              <div class="conversation-top">
                <strong>{{ item.title }}</strong>
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
            <h2>{{ activeConversation?.title }}</h2>
            <p>{{ t('messageCenter.orderTag') }}: {{ activeConversation?.orderNo }}</p>
          </header>

          <div class="thread-messages">
            <article v-for="msg in messages" :key="msg.id" class="chat-bubble" :class="msg.sender">
              <strong>{{ msg.sender === 'admin' ? t('messageCenter.sender.admin') : t('messageCenter.sender.customer') }}</strong>
              <p>{{ msg.content }}</p>
              <span>{{ msg.time }}</span>
            </article>
          </div>

          <footer class="thread-input">
            <textarea v-model="draft" :placeholder="t('portalMessages.inputPlaceholder')" rows="3" />
            <button class="primary-button" type="button" @click="sendMessage">{{ t('messageCenter.actions.send') }}</button>
          </footer>
        </section>
      </section>
    </section>
  </main>
</template>
