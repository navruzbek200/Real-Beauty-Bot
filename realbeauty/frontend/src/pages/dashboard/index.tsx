import { useSessionStore } from '@/entities/session'

export function DashboardPage() {
  const user = useSessionStore((s) => s.user)
  return (
    <div>
      <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
        Xush kelibsiz, {user?.username}
      </h1>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        Chap menyudan bo'limni tanlang.
      </p>
    </div>
  )
}
