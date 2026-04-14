import { apiDelete, apiGet, apiMultipartPost, apiPost, apiPut } from './client'

export interface CustomerDTO {
  id: number
  company_name: string
  contact_name: string
  contact_email: string
  contact_phone: string
  region: string
  status: 'enabled' | 'disabled'
  updated_at: string
}

export interface UserDTO {
  id: number
  username: string
  email: string
  role: 'admin' | 'customer'
  customer: number | null
  customer_name?: string
  is_enabled: boolean
  date_joined: string
  last_login: string | null
}

export interface OrderDTO {
  id: number
  customer: number
  order_no: string
  customer_name?: string
  order_date: string
  amount: string
  description: string
  currency: string
  eta: string | null
  status: 'pending' | 'pending_payment' | 'paid' | 'pending_shipment' | 'shipped' | 'completed'
}

export interface ConfirmationDTO {
  id: number
  task_no: string
  order: number
  order_no?: string
  item_type: string
  item_name: string
  status: 'pending' | 'approved' | 'revise' | 'resubmitted'
  latest_feedback?: string
  updated_at: string
}

export interface FileDTO {
  id: number
  order: number
  file_name: string
  order_no?: string
  file_type: string
  version: string
  size: string
  uploaded_at: string
  visibility: 'customer' | 'internal'
  uploader_name?: string
  file_url?: string
}

export interface LogisticsDTO {
  id: number
  order: number
  order_no?: string
  company: string
  tracking_no: string
  etd: string | null
  eta: string | null
  status: 'preparing' | 'inTransit' | 'customs' | 'delayed' | 'delivered'
  latest_note: string
}

export interface MessageThreadDTO {
  id: number
  title: string
  customer_name?: string
  order_no?: string
  order: number | null
  created_at: string
}

export interface MessageRecordDTO {
  id: number
  thread: number
  parent: number | null
  sender_role: 'admin' | 'customer'
  sender_name?: string
  content: string
  created_at: string
}

export interface OrderItemDTO {
  id: number
  order_no?: string
  sku: string
  name: string
  spec: string
  qty: number
  unit_price: string
  total: string
}

export function fetchCustomers() {
  return apiGet<CustomerDTO[]>('/customers/')
}

export function fetchUsers() {
  return apiGet<UserDTO[]>('/users/')
}

export function updateUser(id: number, payload: Partial<UserDTO>) {
  return apiPut<UserDTO>(`/users/${id}/`, payload)
}

export function fetchCustomer(id: number) {
  return apiGet<CustomerDTO>(`/customers/${id}/`)
}

export function fetchOrders(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<OrderDTO[]>(`/orders/${query}`)
}

export function createOrder(payload: Omit<OrderDTO, 'id' | 'customer_name'>) {
  return apiPost<OrderDTO>('/orders/', payload)
}

export function updateOrder(id: number, payload: Partial<Omit<OrderDTO, 'id' | 'customer_name'>>) {
  return apiPut<OrderDTO>(`/orders/${id}/`, payload)
}

export function deleteOrder(id: number) {
  return apiDelete(`/orders/${id}/`)
}

export function fetchConfirmations(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<ConfirmationDTO[]>(`/confirmations/${query}`)
}

export function createConfirmation(payload: {
  task_no?: string
  order: number
  item_type: string
  item_name: string
  status: ConfirmationDTO['status']
  latest_feedback?: string
}) {
  return apiPost<ConfirmationDTO>('/confirmations/', payload)
}

export function updateConfirmation(id: number, payload: Partial<{
  task_no: string
  order: number
  item_type: string
  item_name: string
  status: ConfirmationDTO['status']
  latest_feedback: string
}>) {
  return apiPut<ConfirmationDTO>(`/confirmations/${id}/`, payload)
}

export function deleteConfirmation(id: number) {
  return apiDelete(`/confirmations/${id}/`)
}

export function fetchFiles(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<FileDTO[]>(`/files/${query}`)
}

export function uploadOrderFile(payload: {
  order: number
  file: File
  file_type: string
  version?: string
  visibility?: FileDTO['visibility']
}) {
  const form = new FormData()
  form.append('order', String(payload.order))
  form.append('file', payload.file)
  form.append('file_type', payload.file_type)
  form.append('version', payload.version || 'v1')
  form.append('visibility', payload.visibility || 'customer')
  return apiMultipartPost<FileDTO>('/files/', form)
}

export function updateFileRecord(id: number, payload: Partial<{
  file_type: string
  version: string
  visibility: FileDTO['visibility']
}>) {
  return apiPut<FileDTO>(`/files/${id}/`, payload)
}

export function deleteFileRecord(id: number) {
  return apiDelete(`/files/${id}/`)
}

export function fetchLogistics(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<LogisticsDTO[]>(`/logistics/${query}`)
}

export function createLogistics(payload: {
  order: number
  company: string
  tracking_no: string
  etd?: string | null
  eta?: string | null
  status: LogisticsDTO['status']
  latest_note?: string
}) {
  return apiPost<LogisticsDTO>('/logistics/', payload)
}

export function updateLogistics(id: number, payload: Partial<{
  order: number
  company: string
  tracking_no: string
  etd: string | null
  eta: string | null
  status: LogisticsDTO['status']
  latest_note: string
}>) {
  return apiPut<LogisticsDTO>(`/logistics/${id}/`, payload)
}

export function deleteLogistics(id: number) {
  return apiDelete(`/logistics/${id}/`)
}

export function fetchMessageThreads(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<MessageThreadDTO[]>(`/messages/${query}`)
}

export function createMessageThread(payload: { customer: number; order: number; title: string }) {
  return apiPost<MessageThreadDTO>('/messages/', payload)
}

export function fetchMessageRecords(threadId: number) {
  return apiGet<MessageRecordDTO[]>(`/message-records/?thread=${threadId}`)
}

export function fetchOrderItems(params?: { order_no?: string }) {
  const query = params?.order_no ? `?order_no=${params.order_no}` : ''
  return apiGet<OrderItemDTO[]>(`/order-items/${query}`)
}

export function createOrderItem(payload: {
  order: number
  sku: string
  name: string
  spec?: string
  qty: number
  unit_price: string
}) {
  return apiPost<OrderItemDTO>('/order-items/', payload)
}

export function updateOrderItem(id: number, payload: Partial<{
  order: number
  sku: string
  name: string
  spec: string
  qty: number
  unit_price: string
}>) {
  return apiPut<OrderItemDTO>(`/order-items/${id}/`, payload)
}

export function deleteOrderItem(id: number) {
  return apiDelete(`/order-items/${id}/`)
}

export function createMessageRecord(threadId: number, content: string, parent?: number) {
  return apiPost<MessageRecordDTO>('/message-records/', {
    thread: threadId,
    content,
    parent: parent || null,
  })
}
