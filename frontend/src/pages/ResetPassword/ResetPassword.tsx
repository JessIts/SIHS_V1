import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import Input from '../../components/ui/Input/Input'
import Button from '../../components/ui/Button/Button'

import {
  resetPassword,
  validateResetToken,
} from '../../services/auth.service'
import { errorMessage } from '../../utils/format'

import './ResetPassword.css'

const MIN_LENGTH = 8

type Estado =
  | { tipo: 'validando' }
  | { tipo: 'invalido'; mensaje: string }
  | { tipo: 'formulario'; email: string }
  | { tipo: 'listo'; mensaje: string }

/**
 * Paso 2 de la recuperación: se abre desde el enlace del correo
 * (/reset-password?token=...) y permite definir la nueva contraseña.
 */
function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const token = searchParams.get('token') ?? ''

  const [estado, setEstado] = useState<Estado>({ tipo: 'validando' })

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Antes de mostrar el formulario se verifica que el enlace siga vigente
  useEffect(() => {
    let active = true

    if (!token) {
      setEstado({
        tipo: 'invalido',
        mensaje: 'El enlace está incompleto. Ábrelo de nuevo desde el correo.',
      })
      return
    }

    validateResetToken(token)
      .then((status) => {
        if (active) {
          setEstado({ tipo: 'formulario', email: status.email })
        }
      })
      .catch((validationError) => {
        if (active) {
          setEstado({
            tipo: 'invalido',
            mensaje: errorMessage(
              validationError,
              'El enlace de recuperación no es válido o ya expiró.',
            ),
          })
        }
      })

    return () => {
      active = false
    }
  }, [token])

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setError('')

    if (password.length < MIN_LENGTH) {
      setError(`La contraseña debe tener al menos ${MIN_LENGTH} caracteres.`)
      return
    }

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setLoading(true)

    try {
      const message = await resetPassword(token, password)

      setEstado({ tipo: 'listo', mensaje: message })

    } catch (submitError) {
      setError(
        errorMessage(
          submitError,
          'No fue posible actualizar la contraseña.',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="reset-password-page">

      <div className="reset-password-page__header">
        <h2>Nueva contraseña</h2>

        {estado.tipo === 'formulario' && (
          <p>
            Crea una contraseña nueva para la cuenta{' '}
            <strong>{estado.email}</strong>.
          </p>
        )}
      </div>

      {estado.tipo === 'validando' && (
        <p className="reset-password-page__muted">
          Verificando el enlace...
        </p>
      )}

      {estado.tipo === 'invalido' && (
        <div className="reset-password-page__notice reset-password-page__notice--error" role="alert">
          <p>{estado.mensaje}</p>

          <Link to="/forgot-password" className="reset-password-page__link">
            Solicitar un enlace nuevo
          </Link>
        </div>
      )}

      {estado.tipo === 'formulario' && (
        <form
          className="reset-password-page__form"
          onSubmit={handleSubmit}
        >
          <Input
            id="password"
            name="password"
            type="password"
            label="Nueva contraseña"
            placeholder="Mínimo 8 caracteres"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="new-password"
            minLength={MIN_LENGTH}
            maxLength={128}
            required
          />

          <Input
            id="confirm_password"
            name="confirm_password"
            type="password"
            label="Confirmar contraseña"
            placeholder="Repite la contraseña"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            autoComplete="new-password"
            required
          />

          {error && (
            <p className="reset-password-page__error">
              {error}
            </p>
          )}

          <Button type="submit" loading={loading}>
            Guardar contraseña
          </Button>
        </form>
      )}

      {estado.tipo === 'listo' && (
        <div className="reset-password-page__notice reset-password-page__notice--success" role="status">
          <p>{estado.mensaje}</p>

          <Button type="button" onClick={() => navigate('/login')}>
            Ir a iniciar sesión
          </Button>
        </div>
      )}

      {estado.tipo !== 'listo' && (
        <Link to="/login" className="reset-password-page__back">
          Volver a iniciar sesión
        </Link>
      )}

    </section>
  )
}

export default ResetPassword
