import { useActionState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

async function loginAction(prev, formData) {
  const email = formData.get('email');
  const password = formData.get('password');
  if (!email || !password) {
    return { error: 'Debes completar email y contraseña.' };
  }
  try {
    const res = await fetch('/login', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (res.redirected) {
      window.location.href = res.url;
      return { error: null };
    }
    const data = await res.json();
    if (!res.ok || data.ok === false) {
      return { error: data.error || 'Credenciales inválidas.' };
    }
    return { error: null };
  } catch {
    return { error: 'Error de conexión.' };
  }
}

export default function Login() {
  const [state, formAction, pending] = useActionState(loginAction, { error: null });

  return (
    <div style={{ height: 'calc(100vh - 80px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', boxSizing: 'border-box', overflow: 'hidden' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', width: '100%', maxWidth: '900px', alignItems: 'stretch', maxHeight: '100%' }}>
        <div style={{ borderRadius: '16px', overflow: 'hidden', display: 'flex', alignItems: 'center' }}>
          <img src="/static/foto_portada.png" alt="Ticket World Cup 2026"
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', maxHeight: 'calc(100vh - 128px)' }} />
        </div>
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Link to="/principal" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '36px', height: '36px', borderRadius: '50%', color: 'var(--md-on-surface)', textDecoration: 'none', transition: 'background 0.15s' }}>
              <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>arrow_back</span>
            </Link>
            <h2 style={{ margin: 0 }}>Ingresar</h2>
          </div>
          <form action={formAction}>
            <div className="form-grid">
              <input name="email" type="email" placeholder="Email" required className="full" />
              <input name="password" type="password" placeholder="Contraseña" required className="full" />
            </div>
            <div className="actions" style={{ marginTop: '16px' }}>
              <button className="btn" type="submit" disabled={pending}>
                {pending ? (
                  <><span className="material-symbols-outlined" style={{ animation: 'spin 0.8s linear infinite' }}>progress_activity</span> Ingresando...</>
                ) : (
                  <><span className="material-symbols-outlined">login</span> Entrar</>
                )}
              </button>
            </div>
            <p style={{ marginTop: '16px', fontSize: '0.88rem', color: 'var(--md-on-surface-variant)' }}>
              ¿No tenés cuenta? <Link to="/registrarse" style={{ color: 'var(--md-primary)', textDecoration: 'none', fontWeight: 500 }}>Registrate acá</Link>
            </p>
          </form>
          {state.error && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="result" style={{ marginTop: '12px' }}
            >
              {state.error}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
