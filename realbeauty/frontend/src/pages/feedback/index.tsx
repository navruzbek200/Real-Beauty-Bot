import { ResourcePage } from '@/widgets/resource-crud'
import { userFeedbackApi, type UserFeedback } from '@/entities/analytics'
import { userFeedbackColumns, userFeedbackFormConfig, type UserFeedbackFormValues } from '@/features/analytics'

export function FeedbackPage() {
  return (
    <ResourcePage<UserFeedback, UserFeedbackFormValues, never, Partial<UserFeedback>>
      title="Fikrlar"
      api={userFeedbackApi}
      queryKey={['feedback']}
      columns={userFeedbackColumns}
      searchPlaceholder="Fikr matni..."
      permissions={{ change: 'analytics.change_userfeedback', delete: '*' }}
      formConfig={userFeedbackFormConfig}
      toUpdatePayload={(v) => v}
    />
  )
}
