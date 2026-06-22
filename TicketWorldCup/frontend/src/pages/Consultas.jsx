import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post, renderJson } from '../api.js';

function tableMarkup(rows) {
  if (!rows || !rows.length) return '<div class="small-note">No hay datos para mostrar.</div>';
  const headers = Object.keys(rows[0]);
  return `<table><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${headers.map(h => `<td>${row[h] ?? ''}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function renderReport(title, rows) {
  return `<div class="pill">${title}</div><div style="margin-top: 12px; overflow-x: auto;">${tableMarkup(rows)}</div>`;
}

export default function Consultas() {
  const { session } = useOutletContext();
  const roles = session?.roles || {};
  const email = session?.email;
  const esPropio = !roles.admin && !roles.funcionario;

  const [qEmail, setQEmail] = useState(email || '');
  const [resConsultas, setResConsultas] = useState('');
  const [eventos, setEventos] = useState([]);
  const [selEvento, setSelEvento] = useState('');
  const [selFunc, setSelFunc] = useState('');
  const [funcs, setFuncs] = useState([]);
  const [resExtras, setResExtras] = useState('');
  const [rank, setRank] = useState('');

  useEffect(() => {
    if (!esPropio) cargarSelectEventos();
  }, []);

  async function verCompras() {
    try {
      const data = await requestJSON(`/usuario/${qEmail}/compras`);
      const compras = data.compras || [];
      if (!compras.length) { setResConsultas('<div class="pill">Compras del usuario</div><div class="small-note" style="margin-top:12px;">No hay compras registradas.</div>'); return; }
      const mostrarPagar = esPropio;
      const filas = compras.map(c => {
        const badgeColor = c.estado === 'pendiente' ? '#b45309' : c.estado === 'confirmada' ? '#1d4ed8' : '#1a7a4a';
        const badgeBg = c.estado === 'pendiente' ? '#fef3c7' : c.estado === 'confirmada' ? '#dbeafe' : '#d1fae5';
        return `<tr>
          <td>#${c.idVenta}</td><td>${c.numero || ''}</td><td>${c.fechaVenta || ''}</td><td>${c.cantidadEntradas}</td>
          <td>$${parseFloat(c.montoTotal).toFixed(2)}</td>
          <td><span style="background:${badgeBg};color:${badgeColor};padding:2px 8px;border-radius:999px;font-size:0.78rem;font-weight:600;">${c.estado}</span></td>
          ${mostrarPagar && c.estado === 'pendiente' ? `<td><button class="btn tonal" style="padding:4px 12px;font-size:0.82rem;" onclick="(async()=>{try{await post('/venta/${c.idVenta}/pagar',{});window.location.reload()}catch(err){alert(err.message)}})()"><span class="material-symbols-outlined" style="font-size:15px;">payments</span> Pagar</button></td>` : ''}
        </tr>`;
      }).join('');
      const thAccion = mostrarPagar ? '<th>Acción</th>' : '';
      setResConsultas(`<div class="pill">Compras del usuario</div><div style="margin-top:12px;overflow-x:auto;"><table><thead><tr><th>ID</th><th>Número</th><th>Fecha</th><th>Entradas</th><th>Total</th><th>Estado</th>${thAccion}</tr></thead><tbody>${filas}</tbody></table></div>`);
    } catch (err) { setResConsultas(err.message); }
  }

  async function verEntradas() {
    try {
      const data = await requestJSON(`/usuario/${qEmail}/entradas`);
      setResConsultas(renderReport('Entradas asignadas', data.entradas));
    } catch (err) { setResConsultas(err.message); }
  }

  async function verTransferencias() {
    try {
      const data = await requestJSON(`/usuario/${qEmail}/transferencias`);
      setResConsultas(renderReport('Transferencias del usuario', data.transferencias));
    } catch (err) { setResConsultas(err.message); }
  }

  async function cargarSelectEventos() {
    try {
      const data = await requestJSON('/eventos');
      const evs = data.eventos || [];
      setEventos(evs);
      if (evs.length) {
        setSelEvento(String(evs[0].idEvento));
        cargarSelectFuncionarios(evs[0].idEvento);
      }
    } catch {}
  }

  async function cargarSelectFuncionarios(idEvento) {
    const evId = idEvento || selEvento;
    if (!evId) { setFuncs([]); return; }
    try {
      const data = await requestJSON(`/eventos/${evId}/funcionarios`);
      setFuncs(data.funcionarios || []);
    } catch {}
  }

  async function verSectoresEvento() {
    if (!selEvento) { setResExtras('Seleccioná un evento primero'); return; }
    try {
      const data = await requestJSON(`/eventos/${selEvento}/sectores`);
      setResExtras(renderReport('Sectores del evento', data.sectores));
    } catch (err) { setResExtras(err.message); }
  }

  async function verCobertura() {
    if (!selEvento) { setResExtras('Seleccioná un evento primero'); return; }
    if (!selFunc) { setResExtras('Seleccioná un funcionario'); return; }
    try {
      const data = await requestJSON(`/funcionario/${encodeURIComponent(selFunc)}/evento/${selEvento}/cobertura`);
      setResExtras(renderReport('Cobertura por sector', data.cobertura));
    } catch (err) { setResExtras(err.message); }
  }

  async function cargarRankings() {
    try {
      const ev = await requestJSON('/ranking/eventos?limite=5');
      const comp = await requestJSON('/ranking/compradores?limite=5');
      setRank(`
        <div class="pill">Eventos más vendidos</div>
        <div style="margin-top: 12px; overflow-x: auto;">${tableMarkup(ev.ranking)}</div>
        <div class="pill" style="margin-top: 18px; display: inline-block;">Mayores compradores</div>
        <div style="margin-top: 12px; overflow-x: auto;">${tableMarkup(comp.ranking)}</div>
      `);
    } catch (err) { setRank(err.message); }
  }

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Consultas</p>
        <h1>Reportes y vistas por usuario</h1>
        <p className="hero-copy">Esta sección permite revisar compras, entradas, transferencias, sectores de evento, rankings y cobertura del funcionario.</p>
      </div>

      <div className="panel">
        <h2>Consultas de usuario</h2>
        {esPropio && <p className="small-note" style={{ marginBottom: '12px' }}>Estás viendo tus propios datos.</p>}
        <div className="form-grid">
          <input placeholder="Email usuario" value={qEmail} onChange={e => setQEmail(e.target.value)}
            className="full"
            readOnly={esPropio}
            style={esPropio ? { background: 'var(--md-surface)', color: 'var(--md-on-surface-variant)', border: '1px solid var(--md-outline-variant)' } : {}}
          />
        </div>
        <div className="actions">
          <button className="btn" onClick={verCompras}><span className="material-symbols-outlined">receipt_long</span> Ver compras</button>
          <button className="btn tonal" onClick={verEntradas}><span className="material-symbols-outlined">confirmation_number</span> Ver entradas</button>
          <button className="btn outlined" onClick={verTransferencias}><span className="material-symbols-outlined">swap_horiz</span> Ver transferencias</button>
        </div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resConsultas }} />
      </div>

      {!esPropio && (
        <>
          <div className="panel">
            <h2>Evento y funcionario</h2>
            <div className="form-grid">
              <select style={{ gridColumn: '1 / -1' }} value={selEvento} onChange={e => { setSelEvento(e.target.value); cargarSelectFuncionarios(e.target.value); }}>
                <option value="">Cargando eventos...</option>
                {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.nombreEvento} — {e.fecha} — {e.estadio}</option>)}
              </select>
              <select style={{ gridColumn: '1 / -1' }} value={selFunc} onChange={e => setSelFunc(e.target.value)}>
                <option value="">Seleccioná un funcionario</option>
                {funcs.map(f => <option key={f.emailFuncionario} value={f.emailFuncionario}>{f.emailFuncionario}</option>)}
              </select>
            </div>
            <div className="actions">
              <button className="btn outlined" onClick={verSectoresEvento}><span className="material-symbols-outlined">map</span> Ver sectores del evento</button>
              <button className="btn tonal" onClick={verCobertura}><span className="material-symbols-outlined">coverage</span> Ver cobertura</button>
            </div>
            <div className="result" dangerouslySetInnerHTML={{ __html: resExtras }} />
          </div>

          <div className="panel" style={{ gridColumn: '1 / -1' }}>
            <h2>Rankings</h2>
            <div className="actions"><button className="btn outlined" onClick={cargarRankings}><span className="material-symbols-outlined">leaderboard</span> Actualizar rankings</button></div>
            <div className="result" dangerouslySetInnerHTML={{ __html: rank }} />
          </div>
        </>
      )}
    </section>
  );
}
