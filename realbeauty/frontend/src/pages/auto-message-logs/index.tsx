import { ResourcePage } from '@/widgets/resource-crud'
import { autoMessageLogApi, type AutoMessageLog } from '@/entities/campaign'
import { autoMessageLogColumns } from '@/features/campaign'

export function AutoMessageLogsPage() {
  return (
    <ResourcePage<AutoMessageLog>
      title="Avto xabarlar jurnali"
      api={autoMessageLogApi}
      queryKey={['auto-message-logs']}
      columns={autoMessageLogColumns}
    />
  )
}
