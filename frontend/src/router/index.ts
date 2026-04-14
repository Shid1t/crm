import { createRouter, createWebHistory } from 'vue-router'

import AdminSettingsView from '../views/AdminSettingsView.vue'
import DashboardView from '../views/DashboardView.vue'
import ConfirmationListView from '../views/ConfirmationListView.vue'
import CustomerListView from '../views/CustomerListView.vue'
import FileCenterView from '../views/FileCenterView.vue'
import LogisticsView from '../views/LogisticsView.vue'
import MessageCenterView from '../views/MessageCenterView.vue'
import PortalConfirmationsView from '../views/PortalConfirmationsView.vue'
import PortalAccountView from '../views/PortalAccountView.vue'
import PortalFilesView from '../views/PortalFilesView.vue'
import PortalHomeView from '../views/PortalHomeView.vue'
import PortalLogisticsView from '../views/PortalLogisticsView.vue'
import PortalMessagesView from '../views/PortalMessagesView.vue'
import PortalOrdersView from '../views/PortalOrdersView.vue'
import LoginView from '../views/LoginView.vue'
import OrderDetailView from '../views/OrderDetailView.vue'
import OrderListView from '../views/OrderListView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: DashboardView,
    },
    {
      path: '/admin/customers',
      name: 'admin-customers',
      component: CustomerListView,
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: OrderListView,
    },
    {
      path: '/admin/orders/:orderNo',
      name: 'admin-order-detail',
      component: OrderDetailView,
    },
    {
      path: '/admin/confirmations',
      name: 'admin-confirmations',
      component: ConfirmationListView,
    },
    {
      path: '/admin/files',
      name: 'admin-files',
      component: FileCenterView,
    },
    {
      path: '/admin/logistics',
      name: 'admin-logistics',
      component: LogisticsView,
    },
    {
      path: '/admin/messages',
      name: 'admin-messages',
      component: MessageCenterView,
    },
    {
      path: '/admin/settings',
      name: 'admin-settings',
      component: AdminSettingsView,
    },
    {
      path: '/portal/home',
      name: 'portal-home',
      component: PortalHomeView,
    },
    {
      path: '/portal/orders',
      name: 'portal-orders',
      component: PortalOrdersView,
    },
    {
      path: '/portal/confirmations',
      name: 'portal-confirmations',
      component: PortalConfirmationsView,
    },
    {
      path: '/portal/files',
      name: 'portal-files',
      component: PortalFilesView,
    },
    {
      path: '/portal/logistics',
      name: 'portal-logistics',
      component: PortalLogisticsView,
    },
    {
      path: '/portal/messages',
      name: 'portal-messages',
      component: PortalMessagesView,
    },
    {
      path: '/portal/account',
      name: 'portal-account',
      component: PortalAccountView,
    },
  ],
})

router.beforeEach((to) => {
  if (to.path === '/login') {
    return true
  }

  const token = localStorage.getItem('crm-access-token')
  const role = localStorage.getItem('crm-user-role')

  if (!token) {
    return '/login'
  }

  if (to.path.startsWith('/admin') && role !== 'admin') {
    return '/portal/home'
  }

  if (to.path.startsWith('/portal') && role !== 'customer') {
    return '/admin/dashboard'
  }

  return true
})
