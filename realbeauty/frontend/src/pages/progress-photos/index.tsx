import { ResourcePage } from '@/widgets/resource-crud'
import { progressPhotoApi, type ProgressPhoto } from '@/entities/analytics'
import { progressPhotoColumns } from '@/features/analytics'

export function ProgressPhotosPage() {
  return (
    <ResourcePage<ProgressPhoto>
      title="Natija rasmlari"
      api={progressPhotoApi}
      queryKey={['progress-photos']}
      columns={progressPhotoColumns}
      permissions={{ delete: '*' }}
    />
  )
}
