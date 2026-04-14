<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import LocaleSwitch from '../components/LocaleSwitch.vue'
import { fetchCurrentUser } from '../api/auth'
import { fetchCustomer } from '../api/resources'
import type { CustomerDTO } from '../api/resources'

const { t } = useI18n()

const loading = ref(true)
const error = ref('')
const profile = ref({
  companyName: '',
  contactName: '',
  email: '',
  phone: '',
  region: '',
})

const menuItems = computed(() => [
  { key: 'home', label: t('portal.menu.home'), to: '/portal/home' },
  { key: 'orders', label: t('portal.menu.orders'), to: '/portal/orders' },
  { key: 'confirmations', label: t('portal.menu.confirmations'), to: '/portal/confirmations' },
  { key: 'files', label: t('portal.menu.files'), to: '/portal/files' },
  { key: 'logistics', label: t('portal.menu.logistics'), to: '/portal/logistics' },
  { key: 'messages', label: t('portal.menu.messages'), to: '/portal/messages' },
  { key: 'account', label: t('portal.menu.account'), to: '/portal/account' },
])

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const user = await fetchCurrentUser()
    if (user.customer_id) {
      const customer: CustomerDTO = await fetchCustomer(user.customer_id)
      profile.value = {
        companyName: customer.company_name,
        contactName: customer.contact_name,
        email: customer.contact_email,
        phone: customer.contact_phone,
        region: customer.region,
      }
    } else {
      profile.value = {
        companyName: '-',
        contactName: user.display_name || user.username,
        email: '-',
        phone: '-',
        region: '-',
      }
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
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
          <RouterLink v-if="item.to" class="nav-item" :class="{ active: item.key === 'account' }" :to="item.to">
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
          <p class="panel-kicker">{{ t('portalAccount.kicker') }}</p>
          <h1>{{ t('portalAccount.title') }}</h1>
          <p>{{ t('portalAccount.subtitle') }}</p>
        </div>

        <div class="header-actions">
          <button class="secondary-button">{{ t('portalAccount.actions.changePassword') }}</button>
          <button class="primary-button">{{ t('portalAccount.actions.save') }}</button>
        </div>
      </header>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <p>{{ t('common.loading') }}</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="primary-button" @click="loadProfile">{{ t('common.retry') }}</button>
      </div>

      <section v-else class="detail-grid">
        <article class="dashboard-card detail-card detail-span-2">
          <div class="card-head">
            <h2>{{ t('portalAccount.sections.profile') }}</h2>
          </div>

          <div class="account-form-grid">
            <label class="field">
              <span>{{ t('portalAccount.fields.companyName') }}</span>
              <input v-model="profile.companyName" type="text" />
            </label>
            <label class="field">
              <span>{{ t('portalAccount.fields.contactName') }}</span>
              <input v-model="profile.contactName" type="text" />
            </label>
            <label class="field">
              <span>{{ t('portalAccount.fields.email') }}</span>
              <input v-model="profile.email" type="email" />
            </label>
            <label class="field">
              <span>{{ t('portalAccount.fields.phone') }}</span>
              <input v-model="profile.phone" type="text" />
            </label>
            <label class="field">
              <span>{{ t('portalAccount.fields.region') }}</span>
              <input v-model="profile.region" type="text" />
            </label>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>