import { useState, type ReactNode } from 'react'

import type { ResourceApi } from '@/shared/lib/create-resource-hooks'
import { createResourceHooks } from '@/shared/lib/create-resource-hooks'
import { useTableQueryState } from '@/shared/lib/use-table-query-state'
import { Button, ConfirmDialog, EmptyState, Input, Pagination, Spinner, Table, TableBody, TableHead, Td, Th, Tr } from '@/shared/ui'
import { hasPermission, useSessionStore } from '@/entities/session'
import type {
  ResourceColumn,
  ResourceFormConfig,
  ResourcePermissions,
} from '@/shared/lib/resource-crud-types'
import { ResourceFormDialog } from './resource-form-dialog'

interface WithId {
  id: number
}

interface ResourcePageProps<
  T extends WithId,
  TFormValues extends Record<string, unknown>,
  TCreate,
  TUpdate,
> {
  title: string
  api: ResourceApi<T, TCreate, TUpdate>
  queryKey: string[]
  columns: ResourceColumn<T>[]
  filterKeys?: string[]
  searchPlaceholder?: string
  permissions?: ResourcePermissions
  formConfig?: ResourceFormConfig<TFormValues>
  toCreatePayload?: (values: TFormValues) => TCreate
  toUpdatePayload?: (values: TFormValues) => TUpdate
  filterBar?: (helpers: ReturnType<typeof useTableQueryState>) => ReactNode
  rowActions?: (item: T) => ReactNode
  createLabel?: string
}

export function ResourcePage<
  T extends WithId,
  TFormValues extends Record<string, unknown> = Record<string, unknown>,
  TCreate = Partial<T>,
  TUpdate = Partial<T>,
>({
  title,
  api,
  queryKey,
  columns,
  filterKeys = [],
  searchPlaceholder = 'Qidirish...',
  permissions,
  formConfig,
  toCreatePayload,
  toUpdatePayload,
  filterBar,
  rowActions,
  createLabel = '+ Qo\'shish',
}: ResourcePageProps<T, TFormValues, TCreate, TUpdate>) {
  const user = useSessionStore((s) => s.user)
  const hooks = createResourceHooks<T, TCreate, TUpdate>(queryKey, api)
  const tableState = useTableQueryState(filterKeys)
  const [editing, setEditing] = useState<T | null>(null)
  const [creating, setCreating] = useState(false)
  const [deleting, setDeleting] = useState<T | null>(null)
  const [formError, setFormError] = useState<string>()

  const listQuery = hooks.useList({
    page: tableState.page,
    page_size: tableState.pageSize,
    search: tableState.search || undefined,
    ordering: tableState.ordering || undefined,
    ...tableState.filters,
  })
  const createMutation = hooks.useCreate()
  const updateMutation = hooks.useUpdate()
  const removeMutation = hooks.useRemove()

  const canAdd = permissions?.add ? hasPermission(user, permissions.add) : false
  const canChange = permissions?.change ? hasPermission(user, permissions.change) : false
  const canDelete = permissions?.delete ? hasPermission(user, permissions.delete) : false

  function toggleSort(field: string) {
    const current = tableState.ordering
    if (current === field) tableState.setOrdering(`-${field}`)
    else if (current === `-${field}`) tableState.setOrdering('')
    else tableState.setOrdering(field)
  }

  function sortDirection(field: string): 'asc' | 'desc' | null {
    if (tableState.ordering === field) return 'asc'
    if (tableState.ordering === `-${field}`) return 'desc'
    return null
  }

  async function handleCreate(values: TFormValues) {
    if (!toCreatePayload) return
    setFormError(undefined)
    try {
      await createMutation.mutateAsync(toCreatePayload(values))
      setCreating(false)
    } catch {
      setFormError("Saqlashda xatolik yuz berdi. Maydonlarni tekshiring.")
    }
  }

  async function handleUpdate(values: TFormValues) {
    if (!editing || !toUpdatePayload) return
    setFormError(undefined)
    try {
      await updateMutation.mutateAsync({ id: editing.id, data: toUpdatePayload(values) })
      setEditing(null)
    } catch {
      setFormError("Saqlashda xatolik yuz berdi. Maydonlarni tekshiring.")
    }
  }

  async function handleDelete() {
    if (!deleting) return
    await removeMutation.mutateAsync(deleting.id)
    setDeleting(null)
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h1>
        {canAdd && formConfig && (
          <Button onClick={() => setCreating(true)}>{createLabel}</Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder={searchPlaceholder}
          value={tableState.rawSearch}
          onChange={(e) => tableState.setSearch(e.target.value)}
          className="max-w-xs"
        />
        {filterBar?.(tableState)}
      </div>

      {listQuery.isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : listQuery.isError ? (
        <EmptyState message="Ma'lumotlarni yuklab bo'lmadi." />
      ) : listQuery.data && listQuery.data.results.length === 0 ? (
        <EmptyState message="Hozircha yozuvlar yo'q." />
      ) : listQuery.data ? (
        <Table>
          <TableHead>
            {columns.map((col) => (
              <Th
                key={col.key}
                sortable={Boolean(col.sortField)}
                sortDirection={col.sortField ? sortDirection(col.sortField) : null}
                onSort={col.sortField ? () => toggleSort(col.sortField as string) : undefined}
              >
                {col.header}
              </Th>
            ))}
            {(canChange || canDelete || rowActions) && <Th>Amallar</Th>}
          </TableHead>
          <TableBody>
            {listQuery.data.results.map((item) => (
              <Tr key={item.id}>
                {columns.map((col) => (
                  <Td key={col.key}>{col.render(item)}</Td>
                ))}
                {(canChange || canDelete || rowActions) && (
                  <Td>
                    <div className="flex gap-2">
                      {canChange && formConfig && (
                        <Button variant="ghost" onClick={() => setEditing(item)}>
                          Tahrirlash
                        </Button>
                      )}
                      {canDelete && (
                        <Button variant="ghost" onClick={() => setDeleting(item)}>
                          O'chirish
                        </Button>
                      )}
                      {rowActions?.(item)}
                    </div>
                  </Td>
                )}
              </Tr>
            ))}
          </TableBody>
        </Table>
      ) : null}

      {listQuery.data && (
        <Pagination
          page={tableState.page}
          pageSize={tableState.pageSize}
          count={listQuery.data.count}
          onPageChange={tableState.setPage}
        />
      )}

      {formConfig && (
        <>
          <ResourceFormDialog
            open={creating}
            title={`Yangi ${title.toLowerCase()}`}
            config={formConfig}
            pending={createMutation.isPending}
            serverError={formError}
            onSubmit={handleCreate}
            onClose={() => {
              setCreating(false)
              setFormError(undefined)
            }}
          />
          <ResourceFormDialog
            open={editing !== null}
            title={`${title} — tahrirlash`}
            config={formConfig}
            initialValues={editing ? formConfig.toFormValues(editing as Record<string, unknown>) : undefined}
            pending={updateMutation.isPending}
            serverError={formError}
            onSubmit={handleUpdate}
            onClose={() => {
              setEditing(null)
              setFormError(undefined)
            }}
          />
        </>
      )}

      <ConfirmDialog
        open={deleting !== null}
        title="O'chirishni tasdiqlang"
        message="Bu yozuvni o'chirmoqchimisiz? Bu amalni ortga qaytarib bo'lmaydi."
        danger
        pending={removeMutation.isPending}
        onConfirm={handleDelete}
        onCancel={() => setDeleting(null)}
      />
    </div>
  )
}
