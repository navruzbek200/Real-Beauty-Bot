import { SettingsFormPage } from '@/widgets/settings-form'
import { globalSettingsApi } from '@/entities/bot-settings'
import { globalSettingsFormConfig } from '@/features/bot-settings'

export function GlobalSettingsPage() {
  return (
    <SettingsFormPage
      title="Umumiy sozlamalar"
      queryKey={['global-settings']}
      api={globalSettingsApi}
      config={globalSettingsFormConfig}
      canEdit
    />
  )
}
