<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { login } from '../api/auth'
import LocaleSwitch from '../components/LocaleSwitch.vue'

const { t } = useI18n()
const router = useRouter()

const form = ref({
  username: '',
  password: '',
  remember: true,
})

const isSubmitting = ref(false)
const feedback = ref('')

const statItems = computed(() => [
  { value: '126+', label: t('login.stats.customers') },
  { value: '348', label: t('login.stats.orders') },
  { value: '7 x 12', label: t('login.stats.service') },
])

const highlightItems = computed(() => [
  {
    key: 'confirm',
    title: t('login.highlights.confirm.title'),
    description: t('login.highlights.confirm.desc'),
  },
  {
    key: 'files',
    title: t('login.highlights.files.title'),
    description: t('login.highlights.files.desc'),
  },
  {
    key: 'trace',
    title: t('login.highlights.trace.title'),
    description: t('login.highlights.trace.desc'),
  },
])

async function submit() {
  if (!form.value.username || !form.value.password) {
    feedback.value = t('login.feedback.invalid')
    return
  }

  isSubmitting.value = true
  try {
    const result = await login({
      username: form.value.username,
      password: form.value.password,
    })

    localStorage.setItem('crm-access-token', result.access)
    localStorage.setItem('crm-refresh-token', result.refresh)
    localStorage.setItem('crm-user-role', result.user.role)

    feedback.value = t('login.feedback.success')

    const target = result.user.role === 'admin' ? '/admin/dashboard' : '/portal/home'
    window.setTimeout(() => {
      void router.push(target)
    }, 300)
  } catch {
    feedback.value = t('login.feedback.invalidCredentials')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="login-shell">
    <section class="login-stage">
      <div class="login-brand-panel">
        <div class="hero-grid" aria-hidden="true">
          <span class="hero-line" />
          <span class="hero-line" />
          <span class="hero-line" />
        </div>
        <div class="hero-glow" aria-hidden="true" />

        <div class="brand-topbar">
          <span class="brand-badge">{{ t('login.badge') }}</span>
          <LocaleSwitch />
        </div>

        <div class="brand-copy">
          <p class="eyebrow">Lithium Tools / Compact Machinery</p>
          <h1>{{ t('login.title') }}</h1>
          <p class="brand-subtitle">
            {{ t('login.subtitle') }}
          </p>
        </div>

        <div class="stats-row">
          <article v-for="item in statItems" :key="item.label" class="stats-card">
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </article>
        </div>

        <div class="highlight-list">
          <article v-for="item in highlightItems" :key="item.key" class="highlight-card">
            <span class="highlight-index" />
            <div>
              <h2>{{ item.title }}</h2>
              <p>{{ item.description }}</p>
            </div>
          </article>
        </div>
      </div>

      <section class="login-panel">
        <div class="panel-header">
          <p class="panel-kicker">Secure Access</p>
          <h2>{{ t('login.panelTitle') }}</h2>
          <p>{{ t('login.panelDesc') }}</p>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <label class="field">
            <span>{{ t('login.username') }}</span>
            <input
              v-model.trim="form.username"
              :placeholder="t('login.usernamePlaceholder')"
              autocomplete="username"
              type="text"
            />
          </label>

          <label class="field">
            <span>{{ t('login.password') }}</span>
            <input
              v-model="form.password"
              :placeholder="t('login.passwordPlaceholder')"
              autocomplete="current-password"
              type="password"
            />
          </label>

          <div class="form-row">
            <label class="checkbox-field">
              <input v-model="form.remember" type="checkbox" />
              <span>{{ t('login.remember') }}</span>
            </label>

            <button class="text-button" type="button">{{ t('login.forgot') }}</button>
          </div>

          <button class="submit-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? t('login.submitLoading') : t('login.submitIdle') }}
          </button>

          <p class="form-hint">{{ t('login.hint') }}</p>
          <p class="form-legal">{{ t('login.legal') }}</p>
          <p class="form-feedback" :class="{ visible: feedback }">{{ feedback }}</p>
        </form>
      </section>
    </section>
  </main>
</template>
