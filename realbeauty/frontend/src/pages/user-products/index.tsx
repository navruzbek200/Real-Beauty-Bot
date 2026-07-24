import { ResourcePage } from '@/widgets/resource-crud'
import { userProductApi, type UserProduct } from '@/entities/customer'
import { userProductColumns, userProductFormConfig, type UserProductFormValues } from '@/features/customer'

export function UserProductsPage() {
  return (
    <ResourcePage<UserProduct, UserProductFormValues, { user: number; product: number }, never>
      title="Sotib olingan mahsulotlar"
      api={userProductApi}
      queryKey={['user-products']}
      columns={userProductColumns}
      permissions={{ add: 'users.add_userproduct', delete: 'users.delete_userproduct' }}
      formConfig={userProductFormConfig}
      toCreatePayload={(v) => v}
    />
  )
}
