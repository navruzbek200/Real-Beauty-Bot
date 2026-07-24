import { ResourcePage } from '@/widgets/resource-crud'
import { discountApi, type Discount } from '@/entities/bot-settings'
import { discountColumns, discountFormConfig, type DiscountFormValues } from '@/features/bot-settings'

// Django's DateField accepts a real date or null — never "". Left blank
// (no expiry), the form's "" must become null or the API 400s the save.
function toDiscountPayload(values: DiscountFormValues): Partial<Discount> {
  return { ...values, valid_until: values.valid_until || null }
}

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
      toCreatePayload={toDiscountPayload}
      toUpdatePayload={toDiscountPayload}
    />
  )
}
