import { useState } from 'react'

import { ResourcePage } from '@/widgets/resource-crud'
import { Button, ConfirmDialog } from '@/shared/ui'
import { broadcastApi, type Broadcast } from '@/entities/campaign'
import { broadcastColumns, broadcastFormConfig, type BroadcastFormValues } from '@/features/campaign'

export function BroadcastsPage() {
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [notice, setNotice] = useState<string>()
  const [confirming, setConfirming] = useState<Broadcast | null>(null)

  async function testToMe(item: Broadcast) {
    setPendingId(item.id)
    try {
      const res = await broadcastApi.testToMe(item.id)
      setNotice(res.detail)
    } catch {
      setNotice('Test yuborilmadi.')
    } finally {
      setPendingId(null)
    }
  }

  async function sendNow() {
    if (!confirming) return
    setPendingId(confirming.id)
    try {
      const res = await broadcastApi.sendNow(confirming.id)
      setNotice(res.detail)
    } catch {
      setNotice('Yuborishda xatolik.')
    } finally {
      setPendingId(null)
      setConfirming(null)
    }
  }

  return (
    <div className="space-y-2">
      {notice && <p className="text-sm text-brand-700">{notice}</p>}
      <ResourcePage<Broadcast, BroadcastFormValues, Partial<Broadcast>, Partial<Broadcast>>
        title="E'lonlar"
        api={broadcastApi}
        queryKey={['broadcasts']}
        columns={broadcastColumns}
        searchPlaceholder="Sarlavha yoki matn..."
        permissions={{ add: '*', change: '*', delete: '*' }}
        formConfig={broadcastFormConfig}
        toCreatePayload={(v) => v}
        toUpdatePayload={(v) => v}
        rowActions={(item) => (
          <>
            <Button variant="ghost" disabled={pendingId === item.id} onClick={() => testToMe(item)}>
              Menga test
            </Button>
            {item.status === 'draft' && (
              <Button variant="ghost" disabled={pendingId === item.id} onClick={() => setConfirming(item)}>
                Yuborish
              </Button>
            )}
          </>
        )}
      />
      <ConfirmDialog
        open={confirming !== null}
        title="E'lonni yuborish"
        message={`"${confirming?.title}" barcha mos xaridorlarga yuboriladi. Bu amalni ortga qaytarib bo'lmaydi.`}
        confirmLabel="Ha, yuborish"
        pending={pendingId === confirming?.id}
        onConfirm={sendNow}
        onCancel={() => setConfirming(null)}
      />
    </div>
  )
}
