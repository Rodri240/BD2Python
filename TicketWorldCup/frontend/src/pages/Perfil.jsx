import { useState, useEffect } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import { requestJSON, renderJson } from '../api.js';

export default function Perfil() {
  const { session } = useOutletContext();
  const navigate = useNavigate();
  const roles = session?.roles || {};
  const email = session?.email;
  const [sectores, setSectores] = useState(null);
  const [compras, setCompras] = useState(null);
  const [entradas, setEntradas] = useState(null);
  const [transferencias, setTransferencias] = useState(null);

  const esFuncionario = roles.funcionario && !roles.admin;

  useEffect(() => {
    if (esFuncionario) {
      cargarSectoresAsignados();
    }
  }, []);

  async function cargarSectoresAsignados() {
    try {
      const data = await requestJSON('/funcionario/' + encodeURIComponent(email) + '/asignaciones');
      setSectores(data.asignaciones || []);
    } catch {
      setSectores([]);
    }
  }

  async function cargarCompras() {
    try {
      const data = await requestJSON('/usuario/' + email + '/compras');
      setCompras(data.compras);
    } catch (err) {
      setCompras([]);
    }
  }

  async function cargarEntradas() {
    try {
      const data = await requestJSON('/usuario/' + email + '/entradas');
      setEntradas(data.entradas);
    } catch {
      setEntradas([]);
    }
  }

  async function cargarTransferencias() {
    try {
      const data = await requestJSON('/usuario/' + email + '/transferencias');
      setTransferencias(data.transferencias);
    } catch {
      setTransferencias([]);
    }
  }

  const handleLogout = async () => {
    try {
      await fetch('/logout', { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' } });
    } catch {}
    sessionStorage.removeItem('ticket_session');
    window.dispatchEvent(new Event('session-update'));
    navigate('/login');
  };

  const rolBadge = () => {
    if (roles.admin) return <span style={{ background: '#1a73e8', color: '#fff', fontSize: '0.72rem', fontWeight: 600, padding: '2px 10px', borderRadius: '999px' }}>Admin</span>;
    if (roles.funcionario) return <span style={{ background: 'var(--md-surface)', color: 'var(--md-on-surface-variant)', fontSize: '0.72rem', fontWeight: 600, padding: '2px 10px', borderRadius: '999px', border: '1px solid var(--md-outline-variant)' }}>Funcionario</span>;
    return <span style={{ background: 'var(--md-surface)', color: 'var(--md-on-surface-variant)', fontSize: '0.72rem', fontWeight: 600, padding: '2px 10px', borderRadius: '999px', border: '1px solid var(--md-outline-variant)' }}>Usuario General</span>;
  };

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Perfil</p>
        <h1>Tu actividad</h1>
        {esFuncionario ? (
          <p className="hero-copy">Estos son los eventos y sectores donde estás asignado como funcionario de validación.</p>
        ) : (
          <p className="hero-copy">Consultá tus compras, entradas y transferencias desde un solo lugar.</p>
        )}
        <div className="badge-row">
          <span className="badge"><span className="material-symbols-outlined">account_circle</span> <strong>{email || 'sin sesión'}</strong></span>
        </div>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--md-on-surface-variant)' }}>manage_accounts</span>
          <span style={{ color: 'var(--md-on-surface-variant)', fontSize: '0.9rem' }}>{email || 'sin sesión'}</span>
          {rolBadge()}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn outlined" onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>logout</span> Cerrar sesión
          </button>
        </div>
      </div>

      {esFuncionario ? (
        <div className="panel" style={{ gridColumn: '1 / -1' }}>
          <h2>Mis sectores asignados</h2>
          {sectores === null ? (
            <div className="result"><span className="small-note">Cargando...</span></div>
          ) : sectores.length === 0 ? (
            <div className="result"><span className="small-note">No tenés sectores asignados todavía.</span></div>
          ) : (
            <div className="result" dangerouslySetInnerHTML={{ __html: renderJson(sectores) }} />
          )}
        </div>
      ) : (
        <>
          <div className="panel list-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>Compras</h2>
              <button className="btn tonal" onClick={cargarCompras} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>receipt_long</span> Cargar
              </button>
            </div>
            <div className="result" dangerouslySetInnerHTML={{ __html: compras ? renderJson(compras) : '<span class="small-note">Presioná "Cargar" para ver tus compras.</span>' }} />
          </div>
          <div className="panel list-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>Entradas</h2>
              <button className="btn tonal" onClick={cargarEntradas} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>confirmation_number</span> Cargar
              </button>
            </div>
            <div className="result" dangerouslySetInnerHTML={{ __html: entradas ? renderJson(entradas) : '<span class="small-note">Presioná "Cargar" para ver tus entradas.</span>' }} />
          </div>
          <div className="panel list-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>Transferencias</h2>
              <button className="btn tonal" onClick={cargarTransferencias} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>swap_horiz</span> Cargar
              </button>
            </div>
            <div className="result" dangerouslySetInnerHTML={{ __html: transferencias ? renderJson(transferencias) : '<span class="small-note">Presioná "Cargar" para ver tus transferencias.</span>' }} />
          </div>
        </>
      )}
    </section>
  );
}
