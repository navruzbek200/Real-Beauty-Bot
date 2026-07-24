import { Button } from './button'
import { Dialog } from './dialog'

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
  pending?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Ha, davom eting",
  danger,
  pending,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Dialog open={open} title={title} onClose={onCancel} widthClassName="max-w-sm">
      <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p>
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="secondary" onClick={onCancel} disabled={pending}>
          Bekor qilish
        </Button>
        <Button variant={danger ? 'danger' : 'primary'} onClick={onConfirm} disabled={pending}>
          {pending ? '...' : confirmLabel}
        </Button>
      </div>
    </Dialog>
  )
}
