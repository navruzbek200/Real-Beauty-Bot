import { ResourcePage } from '@/widgets/resource-crud'
import { campaignLogApi, type CampaignLog } from '@/entities/campaign'
import { campaignLogColumns } from '@/features/campaign'

export function CampaignLogsPage() {
  return (
    <ResourcePage<CampaignLog>
      title="Yuborilgan xabarlar"
      api={campaignLogApi}
      queryKey={['campaign-logs']}
      columns={campaignLogColumns}
      searchPlaceholder="Xaridor ismi yoki telefoni..."
    />
  )
}
