import { apiClient } from '@/shared/api/client'
import type { Paginated } from '@/shared/api/types'
import type {
  LoyaltyAccount,
  LoyaltyListParams,
  LoyaltySettings,
  PointsTransaction,
  Reward,
  RewardRedemption,
} from './model/types'

export const loyaltyAccountApi = {
  async list(params: LoyaltyListParams): Promise<Paginated<LoyaltyAccount>> {
    const { data, error } = await apiClient.GET('/api/v1/loyalty-accounts/', {
      params: { query: params },
    })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<LoyaltyAccount> {
    const { data, error } = await apiClient.GET('/api/v1/loyalty-accounts/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
  async adjust(id: number, body: { adjustment: number; note?: string }): Promise<LoyaltyAccount> {
    const { data, error } = await apiClient.POST('/api/v1/loyalty-accounts/{id}/adjust/', {
      params: { path: { id } },
      body,
    })
    if (error) throw error
    return data
  },
}

export const pointsTransactionApi = {
  async list(params: LoyaltyListParams): Promise<Paginated<PointsTransaction>> {
    const { data, error } = await apiClient.GET('/api/v1/points-transactions/', {
      params: { query: params },
    })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<PointsTransaction> {
    const { data, error } = await apiClient.GET('/api/v1/points-transactions/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
}

export const rewardApi = {
  async list(params: LoyaltyListParams): Promise<Paginated<Reward>> {
    const { data, error } = await apiClient.GET('/api/v1/rewards/', { params: { query: params } })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<Reward> {
    const { data, error } = await apiClient.GET('/api/v1/rewards/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
  async create(body: Partial<Reward>): Promise<Reward> {
    const { data, error } = await apiClient.POST('/api/v1/rewards/', { body: body as Reward })
    if (error) throw error
    return data
  },
  async update(id: number, body: Partial<Reward>): Promise<Reward> {
    const { data, error } = await apiClient.PATCH('/api/v1/rewards/{id}/', {
      params: { path: { id } },
      body,
    })
    if (error) throw error
    return data
  },
  async remove(id: number): Promise<void> {
    const { error } = await apiClient.DELETE('/api/v1/rewards/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
  },
}

export const rewardRedemptionApi = {
  async list(params: LoyaltyListParams): Promise<Paginated<RewardRedemption>> {
    const { data, error } = await apiClient.GET('/api/v1/reward-redemptions/', {
      params: { query: params },
    })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<RewardRedemption> {
    const { data, error } = await apiClient.GET('/api/v1/reward-redemptions/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
  async update(id: number, body: Partial<RewardRedemption>): Promise<RewardRedemption> {
    const { data, error } = await apiClient.PATCH('/api/v1/reward-redemptions/{id}/', {
      params: { path: { id } },
      body,
    })
    if (error) throw error
    return data
  },
}

export const loyaltySettingsApi = {
  async get(): Promise<LoyaltySettings> {
    const { data, error } = await apiClient.GET('/api/v1/settings/loyalty/')
    if (error) throw error
    return data
  },
  async update(body: Partial<LoyaltySettings>): Promise<LoyaltySettings> {
    const { data, error } = await apiClient.PATCH('/api/v1/settings/loyalty/', { body })
    if (error) throw error
    return data
  },
}
