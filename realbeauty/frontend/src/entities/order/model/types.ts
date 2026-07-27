export interface OrderItem {
  id: number
  product: number | null
  product_name: string
  price: number
  quantity: number
  subtotal: number
}

export type OrderStatus = 'new' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'
export type OrderDelivery = 'yandex' | 'bts'

export interface Order {
  id: number
  customer_name: string
  phone_number: string
  telegram_id: number
  delivery_method: OrderDelivery
  delivery_label: string
  address: string
  comment: string
  status: OrderStatus
  status_label: string
  total: number
  items: OrderItem[]
  created_at: string
}
