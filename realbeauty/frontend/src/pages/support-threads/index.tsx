import { useState } from 'react'

import { ResourcePage } from '@/widgets/resource-crud'
import { Button, Dialog, Spinner } from '@/shared/ui'
import { supportThreadApi, type SupportThread } from '@/entities/support'
import { supportThreadColumns } from '@/features/support'
import { useQuery } from '@tanstack/react-query'

function ConversationDialog({ threadId, onClose }: { threadId: number | null; onClose: () => void }) {
  const query = useQuery({
    queryKey: ['support-threads', 'detail', threadId],
    queryFn: () => supportThreadApi.retrieve(threadId as number),
    enabled: threadId !== null,
  })

  return (
    <Dialog open={threadId !== null} title="Yozishmalar" onClose={onClose} widthClassName="max-w-2xl">
      {query.isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-2">
          {(query.data?.messages ?? []).map((msg) => (
            <div
              key={msg.id}
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                msg.direction === 'in'
                  ? 'bg-slate-100 dark:bg-slate-800'
                  : 'ml-auto bg-brand-50 dark:bg-brand-900/30'
              }`}
            >
              <div className="mb-1 text-xs text-slate-400">
                {new Date(msg.created_at).toLocaleString('uz-UZ')}
              </div>
              {msg.text || '📎 fayl'}
            </div>
          ))}
          {(query.data?.messages ?? []).length === 0 && (
            <p className="text-sm text-slate-400">Xabarlar yo'q.</p>
          )}
        </div>
      )}
    </Dialog>
  )
}

export function SupportThreadsPage() {
  const [viewing, setViewing] = useState<number | null>(null)

  return (
    <>
      <ResourcePage<SupportThread>
        title="Murojaatlar"
        api={supportThreadApi}
        queryKey={['support-threads']}
        columns={supportThreadColumns}
        filterKeys={['status', 'awaiting_reply']}
        searchPlaceholder="Foydalanuvchi yoki mavzu..."
        permissions={{ delete: '*' }}
        rowActions={(thread) => (
          <Button variant="ghost" onClick={() => setViewing(thread.id)}>
            Ko'rish
          </Button>
        )}
      />
      <ConversationDialog threadId={viewing} onClose={() => setViewing(null)} />
    </>
  )
}
