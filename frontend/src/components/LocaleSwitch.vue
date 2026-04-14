<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { persistLocale } from '../i18n'

const { locale, t } = useI18n()

const localeOptions = computed(() => [
  { value: 'zh-CN', label: t('common.languages.zh-CN') },
  { value: 'en-US', label: t('common.languages.en-US') },
  { value: 'fil-PH', label: t('common.languages.fil-PH') },
])

function updateLocale(event: Event) {
  const target = event.target as HTMLSelectElement
  locale.value = target.value
  persistLocale(target.value)
  document.documentElement.lang = target.value
}
</script>

<template>
  <label class="locale-switch">
    <span>{{ t('common.language') }}</span>
    <select :value="locale" @change="updateLocale">
      <option v-for="option in localeOptions" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
