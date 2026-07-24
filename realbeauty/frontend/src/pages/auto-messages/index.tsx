import { useState } from 'react'

import { ResourcePage } from '@/widgets/resource-crud'
import { Button } from '@/shared/ui'
import { autoMessageApi, type AutoMessage } from '@/entities/campaign'
import { autoMessageColumns, autoMessageFormConfig, type AutoMessageFormValues } from '@/features/campaign'

export function AutoMessagesPage() {
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [notice, setNotice] = useState<string>()

  async function testToMe(item: AutoMessage) {
    setPendingId(item.id)
    try {
      const res = await autoMessageApi.testToMe(item.id)
      setNotice(res.detail)
    } catch {
      setNotice('Test yuborilmadi.')
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="space-y-2">
      {notice && <p className="text-sm text-brand-700">{notice}</p>}
      <ResourcePage<AutoMessage, AutoMessageFormValues, AutoMessage, Partial<AutoMessage>>
        title="Avtomatik xabarlar"
        api={autoMessageApi}
        queryKey={['auto-messages']}
        columns={autoMessageColumns}
        searchPlaceholder="Nomi yoki matn..."
        permissions={{ add: '*', change: '*', delete: '*' }}
        formConfig={autoMessageFormConfig}
        toCreatePayload={(v) => v as AutoMessage}
        toUpdatePayload={(v) => v}
        rowActions={(item) => (
          <Button variant="ghost" disabled={pendingId === item.id} onClick={() => testToMe(item)}>
            Menga test
          </Button>
        )}
      />
    </div>
  )
}
