import { useState } from 'react'
import { Link } from 'react-router-dom'

import Input from '../../components/ui/Input/Input'
import Button from '../../components/ui/Button/Button'

import { forgotPassword } from '../../services/auth.service'
import { errorMessage } from '../../utils/format'

import './ForgotPassword.css'

/**
 * Paso 1 de la recuperación: el usuario escribe su correo y
 * recibe un enlace para crear una nueva contraseña.
 */
function ForgotPassword() {
  const [email, setEmail] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState('')

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setError('')
    setLoading(true)

    try {
      const message = await forgotPassword(email.trim())

      setSent(message)

    } catch (submitError) {
      setError(
        errorMessage(
          submitError,
          'No fue posible enviar el enlace. Intenta de nuevo.',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="forgot-password-page">

      <div className="forgot-password-page__header">
        <h2>Recuperar contraseña</h2>

        <p>
          Escribe el correo de tu cuenta y te enviaremos un enlace
          para crear una contraseña nueva.
        </p>
      </div>

      {sent ? (
        <div className="forgot-password-page__sent" role="status">
          <p>{sent}</p>

          <p className="forgot-password-page__hint">
            Revisa también la carpeta de spam. El enlace vence en unos minutos
            y solo funciona una vez.
          </p>

          <button
            type="button"
            className="forgot-password-page__link-button"
            onClick={() => setSent('')}
          >
            Enviar a otro correo
          </button>
        </div>
      ) : (
        <form
          className="forgot-password-page__form"
          onSubmit={handleSubmit}
        >
          <Input
            id="email"
            name="email"
            type="email"
            label="Correo electrónico"
            placeholder="correo@ejemplo.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />

          {error && (
            <p className="forgot-password-page__error">
              {error}
            </p>
          )}

          <Button type="submit" loading={loading}>
            Enviar enlace
          </Button>
        </form>
      )}

      <Link to="/login" className="forgot-password-page__back">
        Volver a iniciar sesión
      </Link>

    </section>
  )
}

export default ForgotPassword
