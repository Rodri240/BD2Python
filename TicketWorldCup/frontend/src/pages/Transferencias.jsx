import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post } from '../api.js';

export default function Transferencias() {
  const { session } = useOutletContext();
  const email = session?.email;

  const [emailOrigen, setEmailOrigen] = useState(email || '');
  const [emailDestino, setEmailDestino] = useState('');
  const [entradas, setEntradas] = useState([]);
  const [entradasSel, setEntradasSel] = useState(new Set());
  const [resTransferencia, setResTransferencia] = useState('');
  const [pendientes, setPendientes] = useState([]);
  const [aceptadas, setAceptadas] = useState([]);

  useEffect(() => {
    if (email) {
      setEmailOrigen(email);
      cargarEntradas();
      cargarPendientes();
      cargarAceptadas();
    }
  }, [email]);

  async function cargarPendientes() {
    if (!email) return;
    try {
      const data = await requestJSON('/usuario/' + encodeURIComponent(email) + '/transferencias');
      setPendientes((data.transferencias || []).filter(t => t.estado === 'pendiente'));
    } catch {}
  }

  async function cargarAceptadas() {
    if (!email) return;
    try {
      const data = await requestJSON('/usuario/' + encodeURIComponent(email) + '/transferencias');
      setAceptadas((data.transferencias || []).filter(t => t.estado === 'aceptada'));
    } catch {}
  }

  async function cargarEntradas() {
    const eo = emailOrigen || email;
    if (!eo) { alert('Ingresa un email de origen primero'); return; }
    try {
      const data = await requestJSON('/usuario/' + encodeURIComponent(eo) + '/entradas');
      const todas = data.entradas || [];
      setEntradas(todas.filter(e => e.estado === 'activa' && parseInt(e.cantTransferencias) < 3));
    } catch {}
  }

  function toggleEntrada(id, checked) {
    const s = new Set(entradasSel);
    if (checked) s.add(id); else s.delete(id);
    setEntradasSel(s);
  }

  async function solicitarTransferencia() {
    const ids = Array.from(entradasSel);
    if (!ids.length) return;
    try {
      const res = await post('/transferencia', { emailOrigen: emailOrigen || email, emailDestino, idsEntrada: ids });
      setResTransferencia(`Transferencia solicitada correctamente — ${res.cantidad} entrada(s) enviada(s) a ${emailDestino}.`);
      setEntradasSel(new Set());
      cargarEntradas();
    } catch (err) { setResTransferencia(err.message); }
  }

  async function responderTransferenciaId(id, estado) {
    if (!confirm((estado === 'aceptada' ? 'Aceptar' : 'Rechazar') + ' la transferencia #' + id + '?')) return;
    try {
      await post('/transferencia/' + id, { estado });
      setPendientes([]);
      setTimeout(() => { cargarPendientes(); cargarAceptadas(); }, 2000);
    } catch (err) { alert(err.message); }
  }

  const disponibles = entradas.filter(e => e.estado === 'activa' && parseInt(e.cantTransferencias) < 3);

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Transferencias</p>
        <h1>Flujo de Sesión de entradas</h1>
        <p className="hero-copy">La transferencia queda registrada, se acepta o rechaza, y la entrada cambia de propietario sólo al aceptar.</p>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>Solicitar transferencia</h2>
        <div className="form-grid">
          <input placeholder="Email origen" readOnly style={{ background: 'var(--md-surface)', color: 'var(--md-on-surface-variant)', border: '1px solid var(--md-outline-variant)' }} value={emailOrigen} onChange={e => setEmailOrigen(e.target.value)} />
          <input placeholder="Email destino" value={emailDestino} onChange={e => setEmailDestino(e.target.value)} />
          <div className="actions full" style={{ gridColumn: '1 / -1' }}>
            <button className="btn outlined" onClick={cargarEntradas}><span className="material-symbols-outlined">download</span> Cargar entradas del origen</button>
          </div>
        </div>
        <div className="result" style={{ minHeight: 'auto' }}>
          {disponibles.length === 0 ? (
            <span className="small-note">No hay entradas activas disponibles para transferir.</span>
          ) : (
            <>
              <div style={{ marginBottom: '8px', color: 'var(--md-primary)', fontSize: '0.92rem' }}>{disponibles.length} entrada(s) disponible(s) — selecciona las que quieras transferir</div>
              <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                {disponibles.map(e => (
                  <label key={e.idEntrada} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 0', borderBottom: '1px solid var(--md-outline-variant)', cursor: 'pointer' }}>
                    <input type="checkbox" value={e.idEntrada} checked={entradasSel.has(e.idEntrada)} onChange={(ev) => toggleEntrada(e.idEntrada, ev.target.checked)} />
                    <span><strong>#{e.idEntrada}</strong> — {e.nombreEvento} — {e.fecha} {e.hora || ''} — {e.estadio} — Sector {e.idSector}</span>
                  </label>
                ))}
              </div>
            </>
          )}
        </div>
        <div className="actions">
          <button className="btn" onClick={solicitarTransferencia} disabled={entradasSel.size === 0}>
            <span className="material-symbols-outlined">send</span> Solicitar transferencia{entradasSel.size ? ` (${entradasSel.size} entrada(s))` : ''}
          </button>
        </div>
        <div className="result">{resTransferencia}</div>
      </div>

      <div className="panel">
        <h2>Transferencias pendientes</h2>
        <p className="small-note">Las transferencias que te llegaron aparecen automáticamente abajo.</p>
        <div className="result">
          {pendientes.length === 0 ? <span className="small-note">No tenés transferencias pendientes.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>ID</th><th>Entrada</th><th>Origen</th><th>Fecha</th><th>Acción</th></tr></thead>
                <tbody>
                  {pendientes.map(t => (
                    <tr key={t.idTransferencia}>
                      <td>{t.idTransferencia}</td><td>#{t.idEntrada}</td><td>{t.emailOrigen}</td>
                      <td>{t.fechaTransferencia ? t.fechaTransferencia.slice(0, 16).replace('T', ' ') : ''}</td>
                      <td style={{ display: 'flex', gap: '6px' }}>
                        <button className="btn" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => responderTransferenciaId(t.idTransferencia, 'aceptada')}>Aceptar</button>
                        <button className="btn danger" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => responderTransferenciaId(t.idTransferencia, 'rechazada')}>Rechazar</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="panel">
        <h2>Transferencias aceptadas</h2>
        <p className="small-note">Entradas que recibiste o enviaste y fueron aceptadas.</p>
        <div className="result">
          {aceptadas.length === 0 ? <span className="small-note">No hay transferencias aceptadas todavía.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>ID</th><th>Entrada</th><th>De</th><th>Para</th><th>Fecha</th></tr></thead>
                <tbody>
                  {aceptadas.map(t => (
                    <tr key={t.idTransferencia}>
                      <td>{t.idTransferencia}</td><td>#{t.idEntrada}</td><td>{t.emailOrigen}</td><td>{t.emailDestino}</td>
                      <td>{t.fechaTransferencia ? t.fechaTransferencia.slice(0, 16).replace('T', ' ') : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
