import { ResourcePage } from '@/widgets/resource-crud'
import { pointsTransactionApi, type PointsTransaction } from '@/entities/loyalty'
import { pointsTransactionColumns } from '@/features/loyalty'

export function PointsTransactionsPage() {
  return (
    <ResourcePage<PointsTransaction>
      title="Ball harakatlari"
      api={pointsTransactionApi}
      queryKey={['points-transactions']}
      columns={pointsTransactionColumns}
      filterKeys={['reason']}
      searchPlaceholder="Mijoz ismi yoki izoh..."
    />
  )
}
