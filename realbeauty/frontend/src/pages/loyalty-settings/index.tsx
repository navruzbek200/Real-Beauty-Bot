import { SettingsFormPage } from '@/widgets/settings-form'
import { loyaltySettingsApi } from '@/entities/loyalty'
import { loyaltySettingsFormConfig } from '@/features/loyalty'

export function LoyaltySettingsPage() {
  return (
    <SettingsFormPage
      title="Bonus sozlamalari"
      queryKey={['loyalty-settings']}
      api={loyaltySettingsApi}
      config={loyaltySettingsFormConfig}
      canEdit
    />
  )
}
