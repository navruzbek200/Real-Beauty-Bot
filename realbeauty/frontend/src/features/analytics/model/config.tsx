import { z } from 'zod'

import type { ResourceColumn, ResourceFormConfig } from '@/shared/lib/resource-crud-types'
import { Badge } from '@/shared/ui'
import type { ProgressPhoto, SkinQuizResult, UserFeedback } from '@/entities/analytics'

export const userFeedbackFormSchema = z.object({
  admin_reply: z.string().optional(),
})
export type UserFeedbackFormValues = z.infer<typeof userFeedbackFormSchema>
export const userFeedbackFormConfig: ResourceFormConfig<UserFeedbackFormValues> = {
  schema: userFeedbackFormSchema,
  fields: [
    {
      name: 'admin_reply',
      label: 'Javob (mijozga yuboriladi)',
      type: 'textarea',
      help: 'Saqlaganda mijozga botda yuboriladi.',
    },
  ],
  defaultValues: { admin_reply: '' },
  toFormValues: (item) => ({ admin_reply: (item.admin_reply as string) ?? '' }),
}
export const userFeedbackColumns: ResourceColumn<UserFeedback>[] = [
  { key: 'user_name', header: 'Mijoz', render: (f) => f.user_name },
  { key: 'product_name', header: 'Mahsulot', render: (f) => f.product_name ?? '—' },
  {
    key: 'rating',
    header: 'Baho',
    render: (f) => (f.rating ? '⭐️'.repeat(f.rating) : '—'),
  },
  { key: 'text', header: 'Fikr', render: (f) => (f.text ? f.text.slice(0, 60) : '—') },
  {
    key: 'submitted_at',
    header: 'Vaqt',
    sortField: 'submitted_at',
    render: (f) => new Date(f.submitted_at as string).toLocaleString('uz-UZ'),
  },
  {
    key: 'reply_sent',
    header: 'Javob',
    render: (f) => <Badge tone={f.reply_sent ? 'success' : 'neutral'}>{f.reply_sent ? 'Berildi' : '—'}</Badge>,
  },
]

export const skinQuizResultColumns: ResourceColumn<SkinQuizResult>[] = [
  { key: 'user', header: 'Mijoz ID', render: (r) => r.user },
  { key: 'skin_type', header: 'Teri turi', render: (r) => r.skin_type },
  { key: 'language', header: 'Til', render: (r) => r.language },
  {
    key: 'created_at',
    header: 'Vaqt',
    render: (r) => new Date(r.created_at as string).toLocaleString('uz-UZ'),
  },
]

export const progressPhotoColumns: ResourceColumn<ProgressPhoto>[] = [
  {
    key: 'thumbnail',
    header: 'Rasm',
    render: (p) =>
      p.thumbnail ? (
        <img src={p.thumbnail} alt="" className="h-10 w-10 rounded object-cover" />
      ) : (
        <span className="text-slate-300">Telegramda</span>
      ),
  },
  { key: 'user', header: 'Mijoz ID', render: (p) => p.user },
  { key: 'label', header: 'Turi', render: (p) => (p.label === 'before' ? 'Oldin' : 'Keyin') },
  {
    key: 'submitted_at',
    header: 'Vaqt',
    render: (p) => new Date(p.submitted_at as string).toLocaleString('uz-UZ'),
  },
]
