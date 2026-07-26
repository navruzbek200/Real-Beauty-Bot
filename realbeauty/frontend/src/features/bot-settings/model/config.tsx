import { z } from 'zod'

import type { ResourceColumn, ResourceFormConfig } from '@/shared/lib/resource-crud-types'
import { Badge } from '@/shared/ui'
import type { Discount, GlobalSettings } from '@/entities/bot-settings'

export const discountFormSchema = z.object({
  title: z.string().min(1),
  percent: z.coerce.number().int().min(0).max(100),
  description: z.string().optional(),
  promo_code: z.string().optional(),
  valid_until: z.string().optional(),
  is_active: z.boolean(),
})
export type DiscountFormValues = z.infer<typeof discountFormSchema>
export const discountFormConfig: ResourceFormConfig<DiscountFormValues> = {
  schema: discountFormSchema,
  fields: [
    { name: 'title', label: 'Sarlavha', type: 'text' },
    { name: 'percent', label: 'Chegirma foizi (%)', type: 'number' },
    { name: 'description', label: 'Tavsif', type: 'textarea' },
    { name: 'promo_code', label: 'Promokod', type: 'text' },
    { name: 'valid_until', label: 'Amal qilish muddati', type: 'date', help: 'Ixtiyoriy — bo\'sh qoldirsangiz muddatsiz.' },
    { name: 'is_active', label: 'Faol', type: 'checkbox' },
  ],
  defaultValues: {
    title: '',
    percent: 0,
    description: '',
    promo_code: '',
    valid_until: '',
    is_active: true,
  },
  toFormValues: (item) => ({
    title: (item.title as string) ?? '',
    percent: (item.percent as number) ?? 0,
    description: (item.description as string) ?? '',
    promo_code: (item.promo_code as string) ?? '',
    valid_until: (item.valid_until as string) ?? '',
    is_active: Boolean(item.is_active),
  }),
}
export const discountColumns: ResourceColumn<Discount>[] = [
  { key: 'title', header: 'Sarlavha', render: (d) => d.title },
  { key: 'percent', header: 'Foiz', render: (d) => `${d.percent}%` },
  { key: 'promo_code', header: 'Promokod', render: (d) => d.promo_code || '—' },
  {
    key: 'is_active',
    header: 'Holat',
    render: (d) => <Badge tone={d.is_active ? 'success' : 'neutral'}>{d.is_active ? 'Faol' : "O'chirilgan"}</Badge>,
  },
]

export const globalSettingsFormSchema = z.object({
  birthday_discount_percent: z.coerce.number().int().min(0).max(100),
})
export type GlobalSettingsFormValues = z.infer<typeof globalSettingsFormSchema>
export const globalSettingsFormConfig: ResourceFormConfig<GlobalSettingsFormValues> = {
  schema: globalSettingsFormSchema,
  fields: [
    { name: 'birthday_discount_percent', label: "Tug'ilgan kun chegirmasi (%)", type: 'number' },
  ],
  defaultValues: { birthday_discount_percent: 30 },
  toFormValues: (item) => ({
    birthday_discount_percent: (item.birthday_discount_percent as number) ?? 30,
  }),
}
export type { GlobalSettings }
