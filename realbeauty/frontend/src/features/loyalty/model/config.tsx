import { z } from 'zod'

import type { ResourceColumn, ResourceFormConfig } from '@/shared/lib/resource-crud-types'
import { Badge } from '@/shared/ui'
import type {
  LoyaltyAccount,
  LoyaltySettings,
  PointsTransaction,
  Reward,
  RewardRedemption,
} from '@/entities/loyalty'

const TIER_TONE = { bronze: 'neutral', silver: 'info', gold: 'warning', platinum: 'success' } as const

export const loyaltyAccountColumns: ResourceColumn<LoyaltyAccount>[] = [
  { key: 'user_name', header: 'Mijoz', render: (a) => a.user_name },
  { key: 'balance', header: 'Balans', sortField: 'balance', render: (a) => a.balance },
  { key: 'lifetime_points', header: 'Jami', sortField: 'lifetime_points', render: (a) => a.lifetime_points },
  {
    key: 'tier',
    header: 'Daraja',
    render: (a) => <Badge tone={TIER_TONE[a.tier as keyof typeof TIER_TONE] ?? 'neutral'}>{a.tier}</Badge>,
  },
]

export const pointsTransactionColumns: ResourceColumn<PointsTransaction>[] = [
  { key: 'user_name', header: 'Mijoz', render: (t) => t.user_name },
  {
    key: 'points',
    header: 'Ball',
    render: (t) => (
      <span className={t.points > 0 ? 'text-emerald-600' : 'text-red-600'}>
        {t.points > 0 ? `+${t.points}` : t.points}
      </span>
    ),
  },
  { key: 'reason', header: 'Sabab', render: (t) => t.reason },
  { key: 'note', header: 'Izoh', render: (t) => t.note || '—' },
  { key: 'created_at', header: 'Vaqt', render: (t) => new Date(t.created_at as string).toLocaleString('uz-UZ') },
]

export const rewardFormSchema = z.object({
  title: z.string().min(1),
  description: z.string().optional(),
  cost_points: z.coerce.number().int().min(1),
  stock: z.coerce.number().optional(),
  is_active: z.boolean(),
})
export type RewardFormValues = z.infer<typeof rewardFormSchema>
export const rewardFormConfig: ResourceFormConfig<RewardFormValues> = {
  schema: rewardFormSchema,
  fields: [
    { name: 'title', label: 'Nomi', type: 'text' },
    { name: 'description', label: 'Tavsif', type: 'textarea' },
    { name: 'cost_points', label: 'Narxi (ball)', type: 'number' },
    { name: 'stock', label: 'Qoldiq (bo\'sh = cheklanmagan)', type: 'number' },
    { name: 'is_active', label: 'Faol', type: 'checkbox' },
  ],
  defaultValues: { title: '', description: '', cost_points: 500, stock: undefined, is_active: true },
  toFormValues: (item) => ({
    title: (item.title as string) ?? '',
    description: (item.description as string) ?? '',
    cost_points: (item.cost_points as number) ?? 500,
    stock: (item.stock as number) ?? undefined,
    is_active: Boolean(item.is_active),
  }),
}
export const rewardColumns: ResourceColumn<Reward>[] = [
  { key: 'title', header: 'Nomi', render: (r) => r.title },
  { key: 'cost_points', header: 'Narxi', render: (r) => `${r.cost_points} ball` },
  { key: 'stock', header: 'Qoldiq', render: (r) => (r.stock == null ? '∞' : r.stock) },
  {
    key: 'is_active',
    header: 'Holat',
    render: (r) => <Badge tone={r.is_active ? 'success' : 'neutral'}>{r.is_active ? 'Faol' : "O'chirilgan"}</Badge>,
  },
]

export const rewardRedemptionFormSchema = z.object({ is_used: z.boolean() })
export type RewardRedemptionFormValues = z.infer<typeof rewardRedemptionFormSchema>
export const rewardRedemptionFormConfig: ResourceFormConfig<RewardRedemptionFormValues> = {
  schema: rewardRedemptionFormSchema,
  fields: [{ name: 'is_used', label: 'Ishlatilgan', type: 'checkbox' }],
  defaultValues: { is_used: false },
  toFormValues: (item) => ({ is_used: Boolean(item.is_used) }),
}
export const rewardRedemptionColumns: ResourceColumn<RewardRedemption>[] = [
  { key: 'code', header: 'Kod', render: (r) => r.code },
  { key: 'user_name', header: 'Mijoz', render: (r) => r.user_name },
  { key: 'reward_title', header: "Sovg'a", render: (r) => r.reward_title },
  { key: 'points_spent', header: 'Sarflangan', render: (r) => r.points_spent },
  {
    key: 'is_used',
    header: 'Holat',
    render: (r) => <Badge tone={r.is_used ? 'neutral' : 'success'}>{r.is_used ? 'Ishlatilgan' : 'Kutilmoqda'}</Badge>,
  },
]

export const loyaltySettingsFormSchema = z.object({
  is_enabled: z.boolean(),
  points_registration: z.coerce.number().int().min(0),
  points_purchase: z.coerce.number().int().min(0),
  points_feedback: z.coerce.number().int().min(0),
  points_progress: z.coerce.number().int().min(0),
  points_referral: z.coerce.number().int().min(0),
  points_birthday: z.coerce.number().int().min(0),
  points_quiz: z.coerce.number().int().min(0),
  silver_from: z.coerce.number().int().min(1),
  gold_from: z.coerce.number().int().min(1),
  platinum_from: z.coerce.number().int().min(1),
})
export type LoyaltySettingsFormValues = z.infer<typeof loyaltySettingsFormSchema>
export const loyaltySettingsFormConfig: ResourceFormConfig<LoyaltySettingsFormValues> = {
  schema: loyaltySettingsFormSchema,
  fields: [
    { name: 'is_enabled', label: 'Bonus dasturi yoqilgan', type: 'checkbox' },
    { name: 'points_registration', label: "Ro'yxatdan o'tgani uchun", type: 'number' },
    { name: 'points_purchase', label: 'Har bir xarid uchun', type: 'number' },
    { name: 'points_feedback', label: 'Baho bergani uchun', type: 'number' },
    { name: 'points_progress', label: 'Natija rasmi uchun', type: 'number' },
    { name: 'points_referral', label: "Do'st taklifi uchun", type: 'number' },
    { name: 'points_birthday', label: "Tug'ilgan kun sovg'asi", type: 'number' },
    { name: 'points_quiz', label: 'Teri testi uchun', type: 'number' },
    { name: 'silver_from', label: 'Kumush darajasi (balldan)', type: 'number' },
    { name: 'gold_from', label: 'Oltin darajasi (balldan)', type: 'number' },
    { name: 'platinum_from', label: 'Platina darajasi (balldan)', type: 'number' },
  ],
  defaultValues: {
    is_enabled: true,
    points_registration: 50,
    points_purchase: 100,
    points_feedback: 30,
    points_progress: 50,
    points_referral: 150,
    points_birthday: 200,
    points_quiz: 20,
    silver_from: 1000,
    gold_from: 3000,
    platinum_from: 7000,
  },
  toFormValues: (item) => ({
    is_enabled: Boolean(item.is_enabled),
    points_registration: (item.points_registration as number) ?? 50,
    points_purchase: (item.points_purchase as number) ?? 100,
    points_feedback: (item.points_feedback as number) ?? 30,
    points_progress: (item.points_progress as number) ?? 50,
    points_referral: (item.points_referral as number) ?? 150,
    points_birthday: (item.points_birthday as number) ?? 200,
    points_quiz: (item.points_quiz as number) ?? 20,
    silver_from: (item.silver_from as number) ?? 1000,
    gold_from: (item.gold_from as number) ?? 3000,
    platinum_from: (item.platinum_from as number) ?? 7000,
  }),
}
export type { LoyaltySettings }
