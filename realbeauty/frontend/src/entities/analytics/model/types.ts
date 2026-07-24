import type { Schemas } from '@/shared/api/schema'

export type UserFeedback = Schemas['UserFeedback']
export type SkinQuizResult = Schemas['SkinQuizResult']
export type ProgressPhoto = Schemas['ProgressPhoto']

export interface AnalyticsListParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: string | number | boolean | undefined
}
