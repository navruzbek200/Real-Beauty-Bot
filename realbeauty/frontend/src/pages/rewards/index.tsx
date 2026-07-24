import { ResourcePage } from '@/widgets/resource-crud'
import { rewardApi, type Reward } from '@/entities/loyalty'
import { rewardColumns, rewardFormConfig, type RewardFormValues } from '@/features/loyalty'

export function RewardsPage() {
  return (
    <ResourcePage<Reward, RewardFormValues, Partial<Reward>, Partial<Reward>>
      title="Sovg'alar"
      api={rewardApi}
      queryKey={['rewards']}
      columns={rewardColumns}
      filterKeys={['is_active']}
      searchPlaceholder="Nomi..."
      permissions={{ add: '*', change: '*', delete: '*' }}
      formConfig={rewardFormConfig}
      toCreatePayload={(v) => v}
      toUpdatePayload={(v) => v}
    />
  )
}
