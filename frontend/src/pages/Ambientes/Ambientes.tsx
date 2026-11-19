import CrudPage, {
  type CrudColumn,
  type CrudFilter,
} from '../../components/crud/CrudPage/CrudPage'
import type { FieldConfig, FormValues } from '../../components/crud/EntityForm/EntityForm'

import { ambientesService } from '../../services/academic.service'
import type { Ambiente } from '../../types/academic.types'
import { usePermissions } from '../../hooks/usePermissions'
import { optionalInteger, optionalText, text } from '../../utils/form'
import { opcionesCoordinaciones, opcionesSedes } from '../../utils/options'

const columns: CrudColumn<Ambiente>[] = [
  { header: 'Ambiente', render: (item) => <strong>{item.nombre}</strong> },
  { header: 'Sede', render: (item) => item.sede.nombre },
  { header: 'Capacidad', render: (item) => item.capacidad ?? '—' },
  {
    header: 'Coordinación',
    render: (item) =>
      item.coordinacion?.nombre ?? <span className="crud-page__secondary">Sin asignar</span>,
  },
]

const fields: FieldConfig[] = [
  { name: 'sede_uuid', label: 'Sede', type: 'select', required: true, loadOptions: opcionesSedes },
  { name: 'nombre', label: 'Nombre', required: true, maxLength: 100, placeholder: '202 A' },
  { name: 'capacidad', label: 'Capacidad', type: 'number', min: 1, placeholder: '30' },
  {
    name: 'coordinacion_uuid',
    label: 'Coordinación',
    type: 'select',
    loadOptions: opcionesCoordinaciones,
    placeholder: 'Sin asignar',
    help: 'Solo esta coordinación podrá programar clases en el ambiente.',
    fullWidth: true,
  },
]

const filters: CrudFilter[] = [
  { name: 'sede_uuid', label: 'Sede', loadOptions: opcionesSedes },
]

const adminFilters: CrudFilter[] = [
  ...filters,
  { name: 'coordinacion_uuid', label: 'Coordinación', loadOptions: opcionesCoordinaciones },
]

function toPayload(values: FormValues) {
  return {
    sede_uuid: text(values, 'sede_uuid'),
    nombre: text(values, 'nombre'),
    capacidad: optionalInteger(values, 'capacidad'),
    coordinacion_uuid: optionalText(values, 'coordinacion_uuid'),
  }
}

function Ambientes() {
  const { isCoordinador } = usePermissions()

  return (
    <CrudPage
      title={isCoordinador ? 'Mis ambientes' : 'Ambientes'}
      description={
        isCoordinador
          ? 'Ambientes asignados a tu coordinación: son los únicos que puedes usar en los horarios.'
          : 'Salones y espacios de cada sede, repartidos entre las coordinaciones.'
      }
      entityName="ambiente"
      service={ambientesService}
      columns={columns}
      fields={fields}
      filters={isCoordinador ? filters : adminFilters}
      emptyValues={{ sede_uuid: '', nombre: '', capacidad: '', coordinacion_uuid: '' }}
      toFormValues={(item) => ({
        sede_uuid: item.sede.uuid,
        nombre: item.nombre,
        capacidad: item.capacidad?.toString() ?? '',
        coordinacion_uuid: item.coordinacion?.uuid ?? '',
      })}
      toCreate={toPayload}
      toUpdate={toPayload}
    />
  )
}

export default Ambientes
