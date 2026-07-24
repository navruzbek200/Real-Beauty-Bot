import { ResourcePage } from '@/widgets/resource-crud'
import { appUserApi, type AppUser } from '@/entities/customer'
import { appUserColumns, appUserFormConfig, type AppUserFormValues } from '@/features/customer'

export function AppUsersPage() {
  return (
    <ResourcePage<AppUser, AppUserFormValues, Partial<AppUser>, Partial<AppUser>>
      title="App foydalanuvchilari"
      api={appUserApi}
      queryKey={['app-users']}
      columns={appUserColumns}
      filterKeys={['is_active']}
      searchPlaceholder="Ism yoki telefon..."
      permissions={{ change: 'users.change_appuser' }}
      formConfig={appUserFormConfig}
      toUpdatePayload={(v) => v}
    />
  )
}
