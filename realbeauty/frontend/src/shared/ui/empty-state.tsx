export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-sm text-slate-400">
      <span>{message}</span>
    </div>
  )
}
