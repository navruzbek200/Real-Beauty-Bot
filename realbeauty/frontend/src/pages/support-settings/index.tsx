import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { SettingsFormPage } from '@/widgets/settings-form'
import { Button } from '@/shared/ui'
import { supportSettingsApi } from '@/entities/support'
import { supportSettingsFormConfig } from '@/features/support'

export function SupportSettingsPage() {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState(false)
  const [notice, setNotice] = useState<string>()

  async function testConnection() {
    setPending(true)
    try {
      const result = await supportSettingsApi.testConnection()
      queryClient.setQueryData(['support-settings'], result)
      setNotice(
        result.connection_status === 'ok' ? "Ulanish muvaffaqiyatli ✅" : `Xatolik: ${result.last_error}`,
      )
    } catch {
      setNotice('Ulanib bo\'lmadi.')
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="space-y-3">
      <SettingsFormPage
        title="Telegram guruh"
        queryKey={['support-settings']}
        api={supportSettingsApi}
        config={supportSettingsFormConfig}
        canEdit
      />
      <div className="max-w-xl">
        <Button variant="secondary" onClick={testConnection} disabled={pending}>
          {pending ? 'Tekshirilmoqda...' : 'Ulanishni tekshirish'}
        </Button>
        {notice && <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{notice}</p>}
      </div>
    </div>
  )
}
