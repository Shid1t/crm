import { createI18n } from 'vue-i18n'

import enUS from '../locales/en-US'
import filPH from '../locales/fil-PH'
import zhCN from '../locales/zh-CN'

const STORAGE_KEY = 'crm-locale'

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
  'fil-PH': filPH,
}

const savedLocale = localStorage.getItem(STORAGE_KEY)
const locale = savedLocale && savedLocale in messages ? savedLocale : 'zh-CN'

export const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: 'en-US',
  messages,
})

export function persistLocale(nextLocale: string) {
  localStorage.setItem(STORAGE_KEY, nextLocale)
}

export { STORAGE_KEY }
