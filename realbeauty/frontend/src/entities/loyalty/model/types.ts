import type { Schemas } from '@/shared/api/schema'

export type LoyaltyAccount = Schemas['LoyaltyAccount']
export type LoyaltySettings = Schemas['LoyaltySettings']
export type PointsTransaction = Schemas['PointsTransaction']
export type Reward = Schemas['Reward']
export type RewardRedemption = Schemas['RewardRedemption']

export interface LoyaltyListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: string | number | boolean | undefined
}
