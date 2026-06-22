import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, Outlet, useLocation, useNavigation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import NavigationLoader from './NavigationLoader';

const PUBLIC_ENDPOINTS = ['/login', '/registrarse', '/principal'];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const navigation = useNavigation();
  const prevPath = useRef(location.pathname);
  const isNavigating = navigation.state === 'loading' && prevPath.current !== location.pathname;
  const [session, setSession] = useState(() => {
    const stored = sessionStorage.getItem('ticket_session');
    return stored ? JSON.parse(stored) : null;
  });

  const updateSession = () => {
    const stored = sessionStorage.getItem('ticket_session');
    setSession(stored ? JSON.parse(stored) : null);
  };

  useEffect(() => {
    updateSession();
    const handler = () => updateSession();
    window.addEventListener('storage', handler);
    window.addEventListener('session-update', handler);
    return () => {
      window.removeEventListener('storage', handler);
      window.removeEventListener('session-update', handler);
    };
  }, []);

  const isPublic = PUBLIC_ENDPOINTS.includes(location.pathname) || location.pathname === '/principal';

  const handleLogout = async () => {
    try {
      await fetch('/salir', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' } });
    } catch {}
    sessionStorage.removeItem('ticket_session');
    setSession(null);
    window.dispatchEvent(new Event('session-update'));
    navigate('/login');
  };

  const roles = session?.roles || {};
  const email = session?.email;

  const adminLinks = (
    <>
      <Link to="/">Inicio</Link>
      <Link to="/perfil">Perfil</Link>
      <Link to="/registro">Registro</Link>
      <Link to="/infraestructura">Infraestructura</Link>
      <Link to="/compras">Compras</Link>
      <Link to="/transferencias">Transferencias</Link>
      <Link to="/validacion">Validación</Link>
      <Link to="/consultas">Consultas</Link>
    </>
  );

  const funcLinks = (
    <>
      <Link to="/">Inicio</Link>
      <Link to="/perfil">Perfil</Link>
      <Link to="/validacion">Validación</Link>
    </>
  );

  const generalLinks = (
    <>
      <Link to="/">Inicio</Link>
      <Link to="/perfil">Perfil</Link>
      <Link to="/compras">Compras</Link>
      <Link to="/transferencias">Transferencias</Link>
      <Link to="/consultas">Consultas</Link>
    </>
  );

  const roleBadge = roles.admin
    ? { text: 'Admin', style: { background: 'var(--md-primary)', color: 'var(--md-on-primary)', padding: '2px 8px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 500 } }
    : roles.funcionario
    ? { text: 'Funcionario', style: { background: 'var(--md-secondary-container)', color: 'var(--md-on-secondary-container)', padding: '2px 8px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 500 } }
    : { text: 'Usuario General', style: { background: 'var(--md-surface-variant)', color: 'var(--md-on-surface-variant)', padding: '2px 8px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 500 } };

  if (navigation.state === 'idle') {
    prevPath.current = location.pathname;
  }

  return (
    <div className="wrap">
      <NavigationLoader />
      {!isPublic && (
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div className="brand">
              <div className="brand-icon"><span className="material-symbols-outlined">sports_soccer</span></div>
              <div className="brand-text">
                <strong>Ticket World Cup</strong>
                <span>Demo funcional</span>
              </div>
            </div>
          </div>
          {email ? (
            <div className="session-area">
              <nav className="nav-links">
                {roles.admin ? adminLinks : roles.funcionario ? funcLinks : generalLinks}
              </nav>
              <span className="session-chip">
                <span className="material-symbols-outlined">account_circle</span>
                <strong>{email}</strong>
                <span style={roleBadge.style}>{roleBadge.text}</span>
              </span>
              <button className="logout-btn" onClick={handleLogout}>
                <span className="material-symbols-outlined" style={{ fontSize: '18px', verticalAlign: 'middle' }}>logout</span> Salir
              </button>
            </div>
          ) : (
            <Link className="login-link" to="/login">Acceder</Link>
          )}
        </header>
      )}
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 10, scale: 0.99 }}
          animate={{
            opacity: 1,
            y: 0,
            scale: 1,
            filter: isNavigating ? 'blur(1px)' : 'blur(0px)',
          }}
          exit={{ opacity: 0, y: -8, scale: 0.99 }}
          transition={{ duration: 0.25, ease: [0.25, 0.1, 0.25, 1] }}
        >
          <Outlet context={{ session, setSession, updateSession }} />
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
