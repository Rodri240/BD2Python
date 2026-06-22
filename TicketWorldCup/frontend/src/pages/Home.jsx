import { useState, useEffect, useRef } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { requestJSON, post, renderJson } from '../api.js';

function eventoHTML(e, esFuncionario, hoy) {
  let accion;
  if (esFuncionario) {
    const esHoy = e.fecha === hoy;
    accion = esHoy
      ? `<a class="btn tonal" href="/validacion?evento=${e.idEvento}" style="flex-shrink:0;padding:6px 14px;font-size:0.8rem;text-decoration:none;">
           <span class="material-symbols-outlined" style="font-size:15px;">qr_code_scanner</span> Validar
         </a>`
      : `<span style="flex-shrink:0;font-size:0.78rem;color:var(--md-on-surface-variant);padding:6px 14px;">Disponible el ${e.fecha}</span>`;
  } else {
    accion = `<a class="btn tonal" href="/compras?evento=${e.idEvento}" style="flex-shrink:0;padding:6px 14px;font-size:0.8rem;text-decoration:none;">
      <span class="material-symbols-outlined" style="font-size:15px;">shopping_cart</span> Comprar
    </a>`;
  }
  return `<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--md-surface);border-radius:10px;padding:12px 16px;border:1px solid var(--md-outline-variant);">
    <div style="display:flex;align-items:center;gap:12px;min-width:0;">
      <span class="material-symbols-outlined" style="color:var(--md-primary);flex-shrink:0;">stadium</span>
      <div style="min-width:0;">
        <div style="font-weight:600;font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${e.nombreEvento}</div>
        <div style="font-size:0.78rem;color:var(--md-on-surface-variant);">${e.fecha} · ${e.hora || ''} · ${e.ciudadEstadio || e.estadio || ''}</div>
      </div>
    </div>
    ${accion}
  </div>`;
}

export default function Home() {
  const { session } = useOutletContext();
  const [todosEventos, setTodosEventos] = useState([]);
  const [mostrarTodos, setMostrarTodos] = useState(false);
  const [qrInterval, setQrInterval] = useState(null);
  const qrRef = useRef(null);

  const roles = session?.roles || {};
  const email = session?.email;
  const esFuncionario = roles.funcionario && !roles.admin;
  const hoy = new Date().toISOString().slice(0, 10);

  useEffect(() => {
    cargarProximosEventos();
    return () => {
      if (qrInterval) clearInterval(qrInterval);
    };
  }, []);

  async function cargarProximosEventos() {
    try {
      const data = await requestJSON('/eventos');
      const hoy = new Date().toISOString().slice(0, 10);
      const eventos = (data.eventos || [])
        .filter(e => e.fecha >= hoy)
        .sort((a, b) => a.fecha.localeCompare(b.fecha) || (a.hora || '').localeCompare(b.hora || ''));
      setTodosEventos(eventos);
    } catch {}
  }

  useEffect(() => {
    if (email && !roles.admin && !roles.funcionario) {
      cargarEntradas();
    }
  }, [email]);

  const [entradasActivas, setEntradasActivas] = useState(null);
  const [entradasConsumidas, setEntradasConsumidas] = useState(null);

  async function cargarEntradas() {
    try {
      const data = await requestJSON('/usuario/' + encodeURIComponent(email) + '/entradas');
      const entradas = data.entradas || [];
      setEntradasActivas(entradas.filter(e => e.estado !== 'consumida'));
      setEntradasConsumidas(entradas.filter(e => e.estado === 'consumida'));
    } catch {}
  }

  function renderTablaEntradas(entradas, mostrarBotonQR) {
    if (!entradas || !entradas.length) {
      return <span className="small-note">{mostrarBotonQR ? 'No tenés entradas activas.' : 'No tenés entradas consumidas.'}</span>;
    }
    return (
      <div style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Evento</th>
              <th>Fecha</th>
              <th>Sector</th>
              <th>Estado</th>
              {mostrarBotonQR && <th>Acción</th>}
            </tr>
          </thead>
          <tbody>
            {entradas.map(e => (
              <tr key={e.idEntrada}>
                <td>{e.idEntrada}</td>
                <td>{e.nombreEvento}</td>
                <td>{e.fecha} {e.hora || ''}</td>
                <td>{e.sectorCodigo || 'Sector ' + e.idSector}</td>
                <td>{e.estado}</td>
                {mostrarBotonQR && (
                  <td>
                    <button className="btn" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => mostrarQR(e.idEntrada)}>
                      <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>qr_code</span> Mostrar QR
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  const [qrData, setQrData] = useState(null);
  const [qrEntrada, setQrEntrada] = useState(null);

  async function mostrarQR(idEntrada) {
    setQrEntrada(idEntrada);
    setQrData(null);
    await refrescarQR(idEntrada);
    if (qrInterval) clearInterval(qrInterval);
    const interval = setInterval(() => refrescarQR(idEntrada), 28000);
    setQrInterval(interval);
  }

  async function refrescarQR(idEntrada) {
    try {
      const res = await post('/mi-entrada/' + idEntrada + '/qr', { tiempoVencimiento: 30 });
      const token = res.token;
      setQrData(token);
    } catch {}
  }

  function cerrarQR() {
    if (qrInterval) clearInterval(qrInterval);
    setQrInterval(null);
    setQrEntrada(null);
    setQrData(null);
  }

  const visibles = mostrarTodos ? todosEventos : todosEventos.slice(0, 3);

  return (
    <>
      <section className="page-grid">
        <div className="hero-card">
          <p className="eyebrow">Ticket World Cup</p>
          {esFuncionario ? (
            <>
              <h1>Panel de validación</h1>
              <p className="hero-copy">Revisá los próximos eventos y validá las entradas de los asistentes con tu dispositivo registrado.</p>
              <div className="badge-row">
                <span className="badge"><span className="material-symbols-outlined">qr_code_scanner</span> Escáner QR</span>
                <span className="badge"><span className="material-symbols-outlined">verified_user</span> Cobertura por sector</span>
                <span className="badge"><span className="material-symbols-outlined">devices</span> Dispositivos autorizados</span>
              </div>
              <div className="actions" style={{ marginTop: '18px' }}>
                <Link className="btn tonal" to="/validacion"><span className="material-symbols-outlined">qr_code_scanner</span> Ir a validación</Link>
              </div>
            </>
          ) : (
            <>
              <h1>Tu lugar para el Mundial 2026</h1>
              <p className="hero-copy">Comprá tus entradas, transferilas a quien quieras y presentá tu QR en la puerta. Todo desde acá.</p>
              <div className="badge-row">
                <span className="badge"><span className="material-symbols-outlined">confirmation_number</span> Hasta 5 entradas por compra</span>
                <span className="badge"><span className="material-symbols-outlined">swap_horiz</span> Transferencia entre usuarios</span>
                <span className="badge"><span className="material-symbols-outlined">qr_code</span> QR dinámico en tu celular</span>
              </div>
              <div className="actions" style={{ marginTop: '18px' }}>
                {roles.admin && (
                  <Link className="btn" to="/registro"><span className="material-symbols-outlined">person_add</span> Ir a registro</Link>
                )}
                {!roles.admin && !roles.funcionario && (
                  <>
                    <Link className="btn tonal" to="/compras"><span className="material-symbols-outlined">shopping_cart</span> Comprar entradas</Link>
                    <Link className="btn outlined" to="/consultas"><span className="material-symbols-outlined">bar_chart</span> Ver reportes</Link>
                  </>
                )}
              </div>
            </>
          )}
        </div>

        <div className="panel" style={{ alignSelf: 'start' }}>
          <p className="eyebrow">Próximos eventos</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
            {visibles.length === 0 && <span className="small-note">No hay eventos próximos programados.</span>}
            {visibles.map(e => (
              <div key={e.idEvento} dangerouslySetInnerHTML={{ __html: eventoHTML(e, esFuncionario, hoy) }} />
            ))}
          </div>
          {todosEventos.length > 3 && !mostrarTodos && (
            <div style={{ marginTop: '12px' }}>
              <button className="btn outlined" style={{ width: '100%' }} onClick={() => setMostrarTodos(true)}>
                <span className="material-symbols-outlined">expand_more</span> Ver más eventos
              </button>
            </div>
          )}
        </div>

        {email && !roles.admin && !roles.funcionario && (
          <div style={{ gridColumn: '1 / -1' }}>
            <div className="panel">
              <h2>Entradas activas</h2>
              <p className="small-note" style={{ margin: '-8px 0 12px 0' }}>Seleccioná una entrada para generar y mostrar su código QR.</p>
              {renderTablaEntradas(entradasActivas, true)}
            </div>
            <div className="panel" style={{ marginTop: '16px' }}>
              <h2>Entradas consumidas</h2>
              {renderTablaEntradas(entradasConsumidas, false)}
            </div>
          </div>
        )}
      </section>

      {qrEntrada && (
        <div style={{ display: 'flex', position: 'fixed', inset: 0, zIndex: 1000, background: 'rgba(0,0,0,0.6)', alignItems: 'center', justifyContent: 'center' }} onClick={(e) => { if (e.target === e.currentTarget) cerrarQR(); }}>
          <div style={{ background: 'var(--md-surface)', borderRadius: '12px', padding: '24px', minWidth: '300px', maxWidth: '400px', textAlign: 'center', position: 'relative' }}>
            <button onClick={cerrarQR} style={{ position: 'absolute', top: '8px', right: '12px', background: 'none', border: 'none', color: 'var(--md-on-surface-variant)', cursor: 'pointer', fontSize: '1.4rem' }}>&times;</button>
            {qrData ? (
              <>
                <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', marginBottom: '12px', display: 'inline-block' }}>
                  <img src={'https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=' + encodeURIComponent(qrData.valor)} alt="QR" style={{ display: 'block', width: '250px', height: '250px' }} />
                </div>
                <div style={{ fontSize: '0.85rem', wordBreak: 'break-all', background: 'var(--md-surface)', padding: '8px 12px', borderRadius: '6px', border: '1px solid var(--md-outline-variant)' }}>
                  <strong>Token:</strong> {qrData.valor}
                </div>
                <div style={{ marginTop: '8px' }}><span className="small-note">Válido por {qrData.tiempoVencimiento} segundos — renovando automáticamente</span></div>
              </>
            ) : (
              <span className="small-note">Generando QR...</span>
            )}
          </div>
        </div>
      )}
    </>
  );
}
