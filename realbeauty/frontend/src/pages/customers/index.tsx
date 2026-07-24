import { ResourcePage } from '@/widgets/resource-crud'
import { Select } from '@/shared/ui'
import { customerApi, type Customer } from '@/entities/customer'
import { customerColumns, customerFormConfig, type CustomerFormValues } from '@/features/customer'

export function CustomersPage() {
  return (
    <ResourcePage<Customer, CustomerFormValues, Partial<Customer>, Partial<Customer>>
      title="Xaridorlar"
      api={customerApi}
      queryKey={['customers']}
      columns={customerColumns}
      filterKeys={['is_active', 'source', 'face_condition']}
      searchPlaceholder="Ism, username yoki telefon..."
      permissions={{
        add: 'users.add_telegramuser',
        change: 'users.change_telegramuser',
        delete: 'users.delete_telegramuser',
      }}
      formConfig={customerFormConfig}
      toCreatePayload={(v) => v}
      toUpdatePayload={(v) => v}
      filterBar={(state) => (
        <Select
          value={state.filters.source ?? ''}
          onChange={(e) => state.setFilter('source', e.target.value || null)}
          className="max-w-40"
        >
          <option value="">Barcha manbalar</option>
          <option value="self">O'zi</option>
          <option value="admin">Admin</option>
          <option value="app">Mobil ilova</option>
        </Select>
      )}
    />
  )
}
