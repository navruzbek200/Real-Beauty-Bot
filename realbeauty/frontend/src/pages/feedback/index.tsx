import { ResourcePage } from '@/widgets/resource-crud'
import { Select } from '@/shared/ui'
import { userFeedbackApi, type UserFeedback } from '@/entities/analytics'
import { userFeedbackColumns, userFeedbackFormConfig, type UserFeedbackFormValues } from '@/features/analytics'

export function FeedbackPage() {
  return (
    <ResourcePage<UserFeedback, UserFeedbackFormValues, never, Partial<UserFeedback>>
      title="Mijozlar fikri / Baholar"
      api={userFeedbackApi}
      queryKey={['feedback']}
      columns={userFeedbackColumns}
      filterKeys={['rating']}
      searchPlaceholder="Mijoz yoki fikr matni..."
      permissions={{ change: 'analytics.change_userfeedback', delete: '*' }}
      formConfig={userFeedbackFormConfig}
      toUpdatePayload={(v) => v}
      filterBar={(state) => (
        <Select
          value={state.filters.rating ?? ''}
          onChange={(e) => state.setFilter('rating', e.target.value || null)}
          className="max-w-40"
        >
          <option value="">Barcha baholar</option>
          {[5, 4, 3, 2, 1].map((n) => (
            <option key={n} value={n}>
              {'⭐️'.repeat(n)}
            </option>
          ))}
        </Select>
      )}
    />
  )
}
