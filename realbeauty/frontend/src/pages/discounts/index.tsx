import { ResourcePage } from '@/widgets/resource-crud'
import { discountApi, type Discount } from '@/entities/bot-settings'
import { discountColumns, discountFormConfig, type DiscountFormValues } from '@/features/bot-settings'

export function DiscountsPage() {
  return (
    <ResourcePage<Discount, DiscountFormValues, Partial<Discount>, Partial<Discount>>
      title="Chegirmalar"
      api={discountApi}
      queryKey={['discounts']}
      columns={discountColumns}
      filterKeys={['is_active']}
      searchPlaceholder="Sarlavha yoki promokod..."
      permissions={{ add: '*', change: '*', delete: '*' }}
      formConfig={discountFormConfig}
      toCreatePayload={(v) => v}
      toUpdatePayload={(v) => v}
    />
  )
}
