import { apiClient } from '@/shared/api/client'
import type { ListParams, Paginated } from '@/shared/api/types'
import type { Order } from './model/types'

// The orders endpoints aren't in the generated OpenAPI types yet (regenerate
// with `npm run generate:types` against a running backend to fix); until then
// the calls are cast through a known path shape, same as entities/campaign.
export const orderApi = {
  async list(params: ListParams): Promise<Paginated<Order>> {
    const { data, error } = await apiClient.GET('/api/v1/orders/' as '/api/v1/message-templates/', {
      params: { query: params },
    })
    if (error) throw error
    return data as unknown as Paginated<Order>
  },
  async retrieve(id: number): Promise<Order> {
    const { data, error } = await apiClient.GET(
      '/api/v1/orders/{id}/' as '/api/v1/message-templates/{id}/',
      { params: { path: { id } } },
    )
    if (error) throw error
    return data as unknown as Order
  },
  async update(id: number, body: Partial<Order>): Promise<Order> {
    const { data, error } = await apiClient.PATCH(
      '/api/v1/orders/{id}/' as '/api/v1/message-templates/{id}/',
      { params: { path: { id } }, body: body as never },
    )
    if (error) throw error
    return data as unknown as Order
  },
}
