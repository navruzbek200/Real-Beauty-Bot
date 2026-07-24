import { ResourcePage } from '@/widgets/resource-crud'
import { staffApi, type Staff } from '@/entities/staff'
import { staffColumns, staffFormConfig, toStaffPayload, type StaffFormValues } from '@/features/staff'

export function StaffPage() {
  return (
    <ResourcePage<Staff, StaffFormValues, Staff, Partial<Staff>>
      title="Xodimlar"
      api={staffApi}
      queryKey={['staff']}
      columns={staffColumns}
      searchPlaceholder="Login yoki ism..."
      permissions={{ add: '*', change: '*', delete: '*' }}
      formConfig={staffFormConfig}
      toCreatePayload={(v) => toStaffPayload(v) as unknown as Staff}
      toUpdatePayload={(v) => toStaffPayload(v) as Partial<Staff>}
    />
  )
}
