import { z } from 'zod'

import type { ResourceColumn, ResourceFormConfig } from '@/shared/lib/resource-crud-types'
import type { UserProduct } from '@/entities/customer'

export const userProductFormSchema = z.object({
  user: z.coerce.number().min(1, 'Mijozni tanlang'),
  product: z.coerce.number().min(1, 'Mahsulotni tanlang'),
})
export type UserProductFormValues = z.infer<typeof userProductFormSchema>
export const userProductFormConfig: ResourceFormConfig<UserProductFormValues> = {
  schema: userProductFormSchema,
  fields: [
    { name: 'user', label: 'Mijoz ID', type: 'number' },
    { name: 'product', label: 'Mahsulot ID', type: 'number' },
  ],
  defaultValues: { user: 0, product: 0 },
  toFormValues: (item) => ({
    user: (item.user as number) ?? 0,
    product: (item.product as number) ?? 0,
  }),
}
export const userProductColumns: ResourceColumn<UserProduct>[] = [
  { key: 'user', header: 'Mijoz ID', render: (up) => up.user },
  { key: 'product_name', header: 'Mahsulot', render: (up) => up.product_name },
  {
    key: 'purchased_at',
    header: 'Sana',
    render: (up) => new Date(up.purchased_at as string).toLocaleDateString('uz-UZ'),
  },
]
