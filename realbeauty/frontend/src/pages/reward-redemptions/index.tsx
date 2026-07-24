import { ResourcePage } from '@/widgets/resource-crud'
import { rewardRedemptionApi, type RewardRedemption } from '@/entities/loyalty'
import {
  rewardRedemptionColumns,
  rewardRedemptionFormConfig,
  type RewardRedemptionFormValues,
} from '@/features/loyalty'

export function RewardRedemptionsPage() {
  return (
    <ResourcePage<RewardRedemption, RewardRedemptionFormValues, never, Partial<RewardRedemption>>
      title="Almashtirilgan sovg'alar"
      api={rewardRedemptionApi}
      queryKey={['reward-redemptions']}
      columns={rewardRedemptionColumns}
      filterKeys={['is_used']}
      searchPlaceholder="Kod yoki mijoz..."
      permissions={{ change: 'loyalty.change_rewardredemption' }}
      formConfig={rewardRedemptionFormConfig}
      toUpdatePayload={(v) => v}
    />
  )
}
