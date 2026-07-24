import type { Schemas } from '@/shared/api/schema'

export type Customer = Schemas['TelegramUser']
export type AppUser = Schemas['AppUser']
export type UserProduct = Schemas['UserProduct']

export interface CustomerListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  is_active?: boolean
  source?: 'self' | 'admin' | 'app'
  face_condition?: 'dry' | 'oily' | 'combined' | 'normal' | 'sensitive'
}
