import { Link } from 'react-router-dom';

export default function Principal() {
  return (
    <div style={{
      fontFamily: "'Inter', sans-serif",
      background: '#0f0f0f',
      height: '100vh',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      margin: '-16px -16px 0',
      padding: 0,
      width: 'calc(100% + 32px)',
      position: 'relative',
      left: '-16px',
    }}>
      <nav style={{
        position: 'relative',
        zIndex: 10,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '20px 40px',
      }}>
        <span style={{ color: '#fff', fontWeight: 600, fontSize: '1rem', letterSpacing: '0.01em' }}>
          Ticketing World Cup
        </span>
        <Link to="/login" style={{
          background: '#fff',
          color: '#0f0f0f',
          fontFamily: "'Inter', sans-serif",
          fontSize: '0.88rem',
          fontWeight: 600,
          padding: '10px 28px',
          borderRadius: '999px',
          cursor: 'pointer',
          textDecoration: 'none',
          transition: 'opacity 0.2s',
        }}>Acceder</Link>
      </nav>
      <main style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 40px 32px',
        gap: '48px',
      }}>
        <div style={{
          flex: '0 0 auto',
          width: '700px',
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 24px 64px rgba(0,0,0,0.6)',
        }}>
          <img
            src="/static/foto_portada.png"
            alt="FIFA World Cup 2026"
            style={{ width: '100%', height: 'auto', display: 'block' }}
          />
        </div>
        <div style={{ flex: 1, maxWidth: '400px' }}>
          <p style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.5)',
            marginBottom: '14px',
          }}>Acceso al sistema</p>
          <h1 style={{
            fontSize: '2.2rem',
            fontWeight: 700,
            color: '#fff',
            lineHeight: 1.2,
            marginBottom: '16px',
            maxWidth: 'none',
          }}>Iniciá sesión para entrar a la DEMO</h1>
          <p style={{
            fontSize: '0.95rem',
            color: 'rgba(255,255,255,0.6)',
            lineHeight: 1.6,
            marginBottom: '28px',
          }}>
            El acceso queda guardado en la sesión del navegador para mantenerte autenticado mientras navegás por las páginas del sistema.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {['Sesión persistente', 'Páginas protegidas', 'Login real contra la base'].map(t => (
              <span key={t} style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.78rem',
                fontWeight: 500,
                color: 'rgba(255,255,255,0.75)',
                background: 'rgba(255,255,255,0.08)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '999px',
                padding: '6px 14px',
              }}>{t}</span>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
