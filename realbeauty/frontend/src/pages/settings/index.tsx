import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { ResourcePage } from '@/widgets/resource-crud'
import { SettingsFormPage } from '@/widgets/settings-form'
import { Alert, Button, Tabs, type TabItem } from '@/shared/ui'
import { discountApi, globalSettingsApi, type Discount } from '@/entities/bot-settings'
import { loyaltySettingsApi, rewardApi, type Reward } from '@/entities/loyalty'
import { staffApi, type Staff } from '@/entities/staff'
import { supportAdminApi, supportSettingsApi, type SupportAdmin } from '@/entities/support'
import {
  discountColumns,
  discountFormConfig,
  globalSettingsFormConfig,
  type DiscountFormValues,
} from '@/features/bot-settings'
import {
  loyaltySettingsFormConfig,
  rewardColumns,
  rewardFormConfig,
  type RewardFormValues,
} from '@/features/loyalty'
import { staffColumns, staffFormConfig, toStaffPayload, type StaffFormValues } from '@/features/staff'
import {
  supportAdminColumns,
  supportAdminFormConfig,
  supportSettingsFormConfig,
  type SupportAdminFormValues,
} from '@/features/support'

const TABS: TabItem[] = [
  { key: 'discounts', label: 'Chegirmalar' },
  { key: 'bonus', label: 'Bonus dasturi' },
  { key: 'telegram', label: 'Telegram guruh' },
  { key: 'staff', label: 'Xodimlar' },
]

// Django's PositiveInteger stock wants a number or null — the form keeps it as
// text so "unlimited" can be left blank; "" must become null, not 0.
function toRewardPayload(values: RewardFormValues): Partial<Reward> {
  const { stock, ...rest } = values
  return { ...rest, stock: stock ? Number(stock) : null }
}

// Django's DateField wants a real date or null — never "". Left blank (no
// expiry), the form's "" must become null or the API 400s the save.
function toDiscountPayload(values: DiscountFormValues): Partial<Discount> {
  return { ...values, valid_until: values.valid_until || null }
}

export function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const active = searchParams.get('tab') ?? 'discounts'

  return (
    <div className="space-y-5">
      <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Sozlamalar</h1>
      <Tabs
        tabs={TABS}
        active={active}
        onChange={(key) => setSearchParams({ tab: key }, { replace: true })}
      />

      {active === 'discounts' && <DiscountsTab />}
      {active === 'bonus' && <BonusTab />}
      {active === 'telegram' && <TelegramTab />}
      {active === 'staff' && <StaffTab />}
    </div>
  )
}

function DiscountsTab() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Tug'ilgan kun chegirmasi
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Bot mijozning tug'ilgan kunida shu foizli chegirma xabarini o'zi yuboradi.
          </p>
        </div>
        <SettingsFormPage
          title=""
          queryKey={['global-settings']}
          api={globalSettingsApi}
          config={globalSettingsFormConfig}
          canEdit
        />
      </section>

      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Chegirmalar ro'yxati
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Botdagi «🎁 Chegirmalar» bo'limida mijozlarga ko'rinadi.
          </p>
        </div>
        <ResourcePage<Discount, DiscountFormValues, Partial<Discount>, Partial<Discount>>
          title=""
          api={discountApi}
          queryKey={['discounts']}
          columns={discountColumns}
          filterKeys={['is_active']}
          searchPlaceholder="Sarlavha yoki promokod..."
          permissions={{ add: '*', change: '*', delete: '*' }}
          formConfig={discountFormConfig}
          toCreatePayload={toDiscountPayload}
          toUpdatePayload={toDiscountPayload}
        />
      </section>
    </div>
  )
}

function TelegramTab() {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState(false)
  const [notice, setNotice] = useState<{ tone: 'success' | 'error'; text: string }>()

  async function testConnection() {
    setPending(true)
    try {
      const result = await supportSettingsApi.testConnection()
      queryClient.setQueryData(['support-settings'], result)
      setNotice(
        result.connection_status === 'ok'
          ? { tone: 'success', text: 'Ulanish muvaffaqiyatli' }
          : { tone: 'error', text: `Xatolik: ${result.last_error}` },
      )
    } catch {
      setNotice({ tone: 'error', text: "Ulanib bo'lmadi." })
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Guruh sozlamasi
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Mijoz murojaatlari shu Telegram guruhga tushadi.
          </p>
        </div>
        <SettingsFormPage
          title=""
          queryKey={['support-settings']}
          api={supportSettingsApi}
          config={supportSettingsFormConfig}
          canEdit
        />
        <div className="max-w-xl">
          <Button variant="secondary" onClick={testConnection} disabled={pending}>
            {pending ? 'Tekshirilmoqda...' : 'Ulanishni tekshirish'}
          </Button>
          {notice && (
            <div className="mt-2">
              <Alert tone={notice.tone}>{notice.text}</Alert>
            </div>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Guruh adminlari
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Guruhda mijozga javob bera oladigan xodimlar.
          </p>
        </div>
        <ResourcePage<SupportAdmin, SupportAdminFormValues, SupportAdmin, Partial<SupportAdmin>>
          title=""
          api={supportAdminApi}
          queryKey={['support-admins']}
          columns={supportAdminColumns}
          searchPlaceholder="Ism yoki Telegram ID..."
          permissions={{ add: '*', change: '*', delete: '*' }}
          formConfig={supportAdminFormConfig}
          toCreatePayload={(v) => v as SupportAdmin}
          toUpdatePayload={(v) => v}
        />
      </section>
    </div>
  )
}

function BonusTab() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Ball va keshbek sozlamalari
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Har bir amal uchun beriladigan ball, darajalar va keshbek foizini shu yerdan
            o'zgartirasiz. O'zgarishlar botda darrov ishlaydi.
          </p>
        </div>
        <SettingsFormPage
          title=""
          queryKey={['loyalty-settings']}
          api={loyaltySettingsApi}
          config={loyaltySettingsFormConfig}
          canEdit
        />
      </section>

      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Sovg'alar
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Mijozlar ballarini shu sovg'alarga almashtiradi — botdagi «💎 Bonuslarim»
            bo'limida ko'rinadi.
          </p>
        </div>
        <ResourcePage<Reward, RewardFormValues, Partial<Reward>, Partial<Reward>>
          title=""
          api={rewardApi}
          queryKey={['rewards']}
          columns={rewardColumns}
          filterKeys={['is_active']}
          searchPlaceholder="Sovg'a nomi..."
          permissions={{ add: '*', change: '*', delete: '*' }}
          formConfig={rewardFormConfig}
          toCreatePayload={toRewardPayload}
          toUpdatePayload={toRewardPayload}
        />
      </section>
    </div>
  )
}

function StaffTab() {
  return (
    <ResourcePage<Staff, StaffFormValues, Staff, Partial<Staff>>
      title=""
      api={staffApi}
      queryKey={['staff']}
      columns={staffColumns}
      searchPlaceholder="Login yoki ism..."
      permissions={{ add: '*', change: '*', delete: '*' }}
      formConfig={staffFormConfig}
      toCreatePayload={(v) => toStaffPayload(v) as unknown as Staff}
      toUpdatePayload={(v) => toStaffPayload(v) as Partial<Staff>}
    />
  )
}
