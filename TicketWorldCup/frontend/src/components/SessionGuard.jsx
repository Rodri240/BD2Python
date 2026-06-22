import { useEffect } from 'react';
import { Outlet, useLocation, useOutletContext } from 'react-router-dom';

export default function SessionGuard() {
  const location = useLocation();
  const outletContext = useOutletContext();
  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch('/api/me', { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          if (data.ok && data.email) {
            sessionStorage.setItem('ticket_session', JSON.stringify({ email: data.email, roles: data.roles }));
            window.dispatchEvent(new Event('session-update'));
            return;
          }
        }
      } catch {}
      sessionStorage.removeItem('ticket_session');
      window.dispatchEvent(new Event('session-update'));
      window.location.href = '/login';
    }
    checkSession();
  }, [location]);
  return <Outlet context={outletContext} />;
}
