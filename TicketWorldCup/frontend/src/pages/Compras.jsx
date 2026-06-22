import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post, renderJson } from '../api.js';

export default function Compras() {
  const { session } = useOutletContext();
  const roles = session?.roles || {};
  const email = session?.email;

  const [eventos, setEventos] = useState([]);
  const [compradores, setCompradores] = useState([]);
  const [idEvento, setIdEvento] = useState('');
  const [idSector, setIdSector] = useState('');
  const [cantidad, setCantidad] = useState('');
  const [emailComp, setEmailComp] = useState(email || '');
  const [emailCompAdmin, setEmailCompAdmin] = useState('');
  const [sectores, setSectores] = useState([]);
  const [resCompra, setResCompra] = useState('');
  const [vPend, setVPend] = useState(null);
  const [rank, setRank] = useState('');

  useEffect(() => {
    cargarEventosCompra();
    if (roles.admin) {
      cargarCompradoresAdmin();
      cargarVentasPendientes();
    }
  }, []);

  async function cargarCompradoresAdmin() {
    try {
      const data = await requestJSON('/usuarios/compradores');
      setCompradores(data.compradores || []);
    } catch {}
  }

  async function cargarEventosCompra() {
    try {
      const data = await requestJSON('/eventos');
      const evs = data.eventos || [];
      setEventos(evs);
      const params = new URLSearchParams(window.location.search);
      const eventoParam = params.get('evento');
      const idPresel = eventoParam || (evs.length ? String(evs[0].idEvento) : null);
      if (idPresel) {
        setIdEvento(idPresel);
        cargarSectoresCompra(idPresel);
      }
    } catch {}
  }

  async function cargarSectoresCompra(idEvento) {
    if (!idEvento) { setSectores([]); return; }
    try {
      const data = await requestJSON(`/eventos/${idEvento}/sectores`);
      setSectores(data.sectores || []);
      if (data.sectores?.length && !idSector) setIdSector(String(data.sectores[0].idSector));
    } catch {}
  }

  async function comprarSimple() {
    try {
      const ec = roles.admin ? emailCompAdmin : emailComp || email;
      const r = await post('/comprar', { emailComprador: ec, idEvento, idSector, cantidad });
      setResCompra(`Compra registrada correctamente. N° de venta: ${r.idVenta}`);
      setCantidad('');
      cargarSectoresCompra(idEvento);
      cargarRankings();
    } catch (err) { setResCompra(err.message); }
  }

  async function cargarRankings() {
    try {
      const ev = await requestJSON('/ranking/eventos?limite=5');
      const comp = await requestJSON('/ranking/compradores?limite=5');
      setRank(renderJson({ eventos: ev.ranking, compradores: comp.ranking }));
    } catch (err) { setRank(err.message); }
  }

  async function cargarVentasPendientes() {
    try {
      const data = await requestJSON('/ventas/pendientes');
      setVPend(data.ventas || []);
    } catch {}
  }

  async function avanzarVenta(idVenta, tipo) {
    try {
      const ruta = tipo === 'pedido' ? `/venta/${idVenta}/confirmar-pedido` : `/venta/${idVenta}/confirmar-pago`;
      await post(ruta, {});
      await cargarVentasPendientes();
    } catch (err) { alert(err.message); }
  }

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Compras</p>
        <h1>Venta individual y múltiple</h1>
        <p className="hero-copy">Desde esta página se prueba el límite de 5 entradas por transacción y el cálculo con comisión vigente.</p>
      </div>

      <div className="panel">
        <h2>Compra:</h2>
        <div className="form-grid">
          {roles.admin ? (
            <>
              <input placeholder="Email comprador" style={{ display: 'none' }} />
              <select className="full" value={emailCompAdmin} onChange={e => setEmailCompAdmin(e.target.value)}>
                <option value="">Cargando compradores...</option>
                {compradores.map(c => <option key={c.email} value={c.email}>{c.email} {c.estadoVerifIdentidad ? `| ${c.estadoVerifIdentidad}` : ''}</option>)}
              </select>
            </>
          ) : (
            <input placeholder="Email comprador" value={emailComp || email} className="full" readOnly />
          )}
          <select className="full" value={idEvento} onChange={e => { setIdEvento(e.target.value); cargarSectoresCompra(e.target.value); }}>
            <option value="">Cargando eventos...</option>
            {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.idEvento} | {e.nombreEvento} | {e.fecha} | {e.hora || ''}</option>)}
          </select>
          <select className="full" value={idSector} onChange={e => setIdSector(e.target.value)}>
            <option value="">Selecciona un sector</option>
            {sectores.map(s => <option key={s.idSector} value={s.idSector}>Sector {s.codigo} | ID {s.idSector} | {s.entradasDisponibles} libres | ${s.costoEntrada}</option>)}
          </select>
          <input placeholder="Cantidad" value={cantidad} onChange={e => setCantidad(e.target.value)} />
        </div>
        <div className="actions"><button className="btn" onClick={comprarSimple}><span className="material-symbols-outlined">shopping_cart_checkout</span> Comprar</button></div>
        <div className="result">{resCompra}</div>
      </div>

      {roles.admin && (
        <div className="panel" style={{ gridColumn: '1 / -1' }}>
          <h2>Ventas pendientes de pago</h2>
          <p className="small-note" style={{ marginBottom: '12px' }}>Las ventas se crean en estado <strong>pendiente</strong>. Confirmá el pago para cambiarlas a <strong>paga</strong>.</p>
          <div className="actions"><button className="btn outlined" onClick={cargarVentasPendientes}><span className="material-symbols-outlined">refresh</span> Actualizar</button></div>
          <div className="result">
            {vPend === null ? <span className="small-note">Presioná "Actualizar" para cargar.</span> : vPend.length === 0 ? <span className="small-note">No hay ventas pendientes.</span> : (
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead><tr><th>ID</th><th>Número</th><th>Comprador</th><th>Entradas</th><th>Total</th><th>Fecha</th><th>Estado</th><th>Acción</th></tr></thead>
                  <tbody>
                    {vPend.map(v => (
                      <tr key={v.idVenta}>
                        <td>#{v.idVenta}</td><td>{v.numero}</td><td>{v.emailComprador}</td><td>{v.cantidadEntradas}</td>
                        <td>${parseFloat(v.montoTotal).toFixed(2)}</td><td>{v.fechaVenta || ''}</td>
                        <td><span style={{ background: v.estado === 'pendiente' ? '#fef3c7' : '#dbeafe', color: v.estado === 'pendiente' ? '#b45309' : '#1d4ed8', padding: '2px 8px', borderRadius: '999px', fontSize: '0.78rem', fontWeight: 600 }}>{v.estado}</span></td>
                        <td>{v.estado === 'pendiente'
                          ? <button className="btn outlined" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => avanzarVenta(v.idVenta, 'pedido')}><span className="material-symbols-outlined" style={{ fontSize: '16px' }}>check_circle</span> Confirmar pedido</button>
                          : <button className="btn" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => avanzarVenta(v.idVenta, 'pago')}><span className="material-symbols-outlined" style={{ fontSize: '16px' }}>payments</span> Confirmar pago</button>
                        }</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>Rankings</h2>
        <div className="actions"><button className="btn outlined" onClick={cargarRankings}><span className="material-symbols-outlined">leaderboard</span> Actualizar rankings</button></div>
        <div className="result" dangerouslySetInnerHTML={{ __html: rank }} />
      </div>
    </section>
  );
}
