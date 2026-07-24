import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { ResourcePage } from '@/widgets/resource-crud'
import { Button, Dialog, FieldError, Input, Label } from '@/shared/ui'
import { isSuperUser, useSessionStore } from '@/entities/session'
import { loyaltyAccountApi, type LoyaltyAccount } from '@/entities/loyalty'
import { loyaltyAccountColumns } from '@/features/loyalty'

function AdjustDialog({ account, onClose }: { account: LoyaltyAccount | null; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [adjustment, setAdjustment] = useState('')
  const [note, setNote] = useState('')
  const [error, setError] = useState<string>()
  const [pending, setPending] = useState(false)

  async function submit() {
    if (!account) return
    const delta = Number(adjustment)
    if (!delta) {
      setError("Raqam kiriting (masalan: 100 yoki -50).")
      return
    }
    setPending(true)
    setError(undefined)
    try {
      await loyaltyAccountApi.adjust(account.id, { adjustment: delta, note })
      queryClient.invalidateQueries({ queryKey: ['loyalty-accounts'] })
      setAdjustment('')
      setNote('')
      onClose()
    } catch {
      setError("Balans yetarli emas yoki xatolik yuz berdi.")
    } finally {
      setPending(false)
    }
  }

  return (
    <Dialog open={account !== null} title="Ballni qo'lda o'zgartirish" onClose={onClose} widthClassName="max-w-sm">
      <div className="space-y-4">
        <div>
          <Label htmlFor="adjustment">Miqdor (+/-)</Label>
          <Input id="adjustment" value={adjustment} onChange={(e) => setAdjustment(e.target.value)} placeholder="masalan: 100 yoki -50" />
        </div>
        <div>
          <Label htmlFor="note">Izoh</Label>
          <Input id="note" value={note} onChange={(e) => setNote(e.target.value)} />
        </div>
        <FieldError message={error} />
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={pending}>
            Bekor qilish
          </Button>
          <Button onClick={submit} disabled={pending}>
            {pending ? 'Saqlanmoqda...' : 'Saqlash'}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

export function LoyaltyAccountsPage() {
  const [adjusting, setAdjusting] = useState<LoyaltyAccount | null>(null)
  const user = useSessionStore((s) => s.user)
  const canAdjust = isSuperUser(user)

  return (
    <>
      <ResourcePage<LoyaltyAccount>
        title="Bonus hisoblari"
        api={loyaltyAccountApi}
        queryKey={['loyalty-accounts']}
        columns={loyaltyAccountColumns}
        filterKeys={['tier']}
        searchPlaceholder="Mijoz ismi yoki telefoni..."
        rowActions={
          canAdjust
            ? (account) => (
                <Button variant="ghost" onClick={() => setAdjusting(account)}>
                  Tuzatish
                </Button>
              )
            : undefined
        }
      />
      <AdjustDialog account={adjusting} onClose={() => setAdjusting(null)} />
    </>
  )
}
