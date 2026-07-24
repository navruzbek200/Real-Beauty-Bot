import { apiClient } from '@/shared/api/client'
import type { Paginated } from '@/shared/api/types'
import type { AnalyticsListParams, ProgressPhoto, SkinQuizResult, UserFeedback } from './model/types'

export const userFeedbackApi = {
  async list(params: AnalyticsListParams): Promise<Paginated<UserFeedback>> {
    const { data, error } = await apiClient.GET('/api/v1/feedback/', { params: { query: params } })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<UserFeedback> {
    const { data, error } = await apiClient.GET('/api/v1/feedback/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
  async update(id: number, body: Partial<UserFeedback>): Promise<UserFeedback> {
    const { data, error } = await apiClient.PATCH('/api/v1/feedback/{id}/', {
      params: { path: { id } },
      body,
    })
    if (error) throw error
    return data
  },
  async remove(id: number): Promise<void> {
    const { error } = await apiClient.DELETE('/api/v1/feedback/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
  },
}

export const skinQuizResultApi = {
  async list(params: AnalyticsListParams): Promise<Paginated<SkinQuizResult>> {
    const { data, error } = await apiClient.GET('/api/v1/skin-quiz-results/', {
      params: { query: params },
    })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<SkinQuizResult> {
    const { data, error } = await apiClient.GET('/api/v1/skin-quiz-results/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
}

export const progressPhotoApi = {
  async list(params: AnalyticsListParams): Promise<Paginated<ProgressPhoto>> {
    const { data, error } = await apiClient.GET('/api/v1/progress-photos/', {
      params: { query: params },
    })
    if (error) throw error
    return data
  },
  async retrieve(id: number): Promise<ProgressPhoto> {
    const { data, error } = await apiClient.GET('/api/v1/progress-photos/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
    return data
  },
  async remove(id: number): Promise<void> {
    const { error } = await apiClient.DELETE('/api/v1/progress-photos/{id}/', {
      params: { path: { id } },
    })
    if (error) throw error
  },
}
