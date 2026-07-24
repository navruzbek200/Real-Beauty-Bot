import { ResourcePage } from '@/widgets/resource-crud'
import { supportAdminApi, type SupportAdmin } from '@/entities/support'
import { supportAdminColumns, supportAdminFormConfig, type SupportAdminFormValues } from '@/features/support'

export function SupportAdminsPage() {
  return (
    <ResourcePage<SupportAdmin, SupportAdminFormValues, SupportAdmin, Partial<SupportAdmin>>
      title="Guruh adminlari"
      api={supportAdminApi}
      queryKey={['support-admins']}
      columns={supportAdminColumns}
      searchPlaceholder="Ism yoki Telegram ID..."
      permissions={{ add: '*', change: '*', delete: '*' }}
      formConfig={supportAdminFormConfig}
      toCreatePayload={(v) => v as SupportAdmin}
      toUpdatePayload={(v) => v}
    />
  )
}
