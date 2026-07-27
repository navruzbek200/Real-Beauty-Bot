import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { ResourcePage } from '@/widgets/resource-crud'
import { Alert, Button, Select } from '@/shared/ui'
import { orderApi, type Order, type OrderStatus } from '@/entities/order'
import { ORDER_STATUS, orderColumns, orderFormConfig, type OrderFormValues } from '@/features/order'

type Notice = { tone: 'success' | 'error'; text: string }

const STATUS_FILTER: { value: string; label: string }[] = [
  { value: '', label: 'Barcha holatlar' },
  { value: 'new', label: '🆕 Yangi' },
  { value: 'confirmed', label: '☎️ Tasdiqlangan' },
  { value: 'shipped', label: "🚚 Yo'lda" },
  { value: 'delivered', label: '✅ Yetkazildi' },
  { value: 'cancelled', label: '❌ Bekor qilingan' },
]

export function OrdersPage() {
  const queryClient = useQueryClient()
  const [pendingId, setPendingId] = useState<number | null>(null)
  const [notice, setNotice] = useState<Notice>()

  async function setStatus(order: Order, status: OrderStatus) {
    setPendingId(order.id)
    setNotice(undefined)
    try {
      await orderApi.update(order.id, { status })
      await queryClient.invalidateQueries({ queryKey: ['orders'] })
      setNotice({
        tone: 'success',
        text: `Buyurtma #${order.id} → ${ORDER_STATUS[status].label}`,
      })
    } catch {
      setNotice({ tone: 'error', text: "Holatni o'zgartirib bo'lmadi. Qayta urinib ko'ring." })
    } finally {
      setPendingId(null)
    }
  }

  return (
    <div className="space-y-3">
      <Alert tone="info">
        Buyurtmalar Mini Appdagi 🛒 savatchadan tushadi va Telegram guruhga ham boradi.
        Ish tartibi: mijozga qo'ng'iroq qiling → <b>Tasdiqlash</b> → jo'natgach{' '}
        <b>Yo'lga chiqdi</b> → qo'lga tekkach <b>Yetkazildi</b>.
      </Alert>
      {notice && (
        <Alert tone={notice.tone} onDismiss={() => setNotice(undefined)}>
          {notice.text}
        </Alert>
      )}
      <ResourcePage<Order, OrderFormValues, Partial<Order>, Partial<Order>>
        title="Buyurtmalar"
        api={orderApi}
        queryKey={['orders']}
        columns={orderColumns}
        filterKeys={['status']}
        searchPlaceholder="Ism, telefon yoki manzil..."
        permissions={{ change: 'orders.change_order' }}
        formConfig={orderFormConfig}
        toUpdatePayload={(v) => v}
        filterBar={(state) => (
          <Select
            value={state.filters.status ?? ''}
            onChange={(e) => state.setFilter('status', e.target.value || null)}
            className="max-w-48"
          >
            {STATUS_FILTER.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
        )}
        rowActions={(item) => {
          const next = ORDER_STATUS[item.status]?.next
          return (
            <>
              {next && (
                <Button
                  size="sm"
                  loading={pendingId === item.id}
                  onClick={() => setStatus(item, next.to)}
                >
                  {next.action}
                </Button>
              )}
              {(item.status === 'new' || item.status === 'confirmed') && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/30"
                  disabled={pendingId === item.id}
                  onClick={() => setStatus(item, 'cancelled')}
                >
                  Bekor
                </Button>
              )}
            </>
          )
        }}
      />
    </div>
  )
}
