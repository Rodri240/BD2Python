import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post } from '../api.js';

export default function Validacion() {
  const { session } = useOutletContext();
  const roles = session?.roles || {};
  const email = session?.email;

  const [eventos, setEventos] = useState([]);
  const [leIdEvento, setLeIdEvento] = useState('');
  const [vaIdEvento, setVaIdEvento] = useState('');
  const [cobIdEvento, setCobIdEvento] = useState('');
  const [vIdDispositivo, setVIdDispositivo] = useState('');
  const [dispositivos, setDispositivos] = useState([]);
  const [dispositivosReg, setDispositivosReg] = useState([]);
  const [ultimoDisp, setUltimoDisp] = useState(null);
  const [ultimoEmail, setUltimoEmail] = useState(null);
  const [sectoresBanner, setSectoresBanner] = useState('');
  const [pendientes, setPendientes] = useState(null);
  const [validadas, setValidadas] = useState(null);
  const [cobertura, setCobertura] = useState(null);
  const [resDisp, setResDisp] = useState('');
  const [dMac, setDMac] = useState('');
  const [dAlias, setDAlias] = useState('');
  const [dEmailFunc, setDEmailFunc] = useState(email || '');

  useEffect(() => {
    cargarEventos();
    cargarDispositivos();
  }, []);

  async function cargarEventos() {
    try {
      const data = await requestJSON('/eventos');
      const evs = data.eventos || [];
      setEventos(evs);
      const params = new URLSearchParams(window.location.search);
      const eventoParam = params.get('evento');
      if (eventoParam) {
        setLeIdEvento(eventoParam);
        setVaIdEvento(eventoParam);
        setCobIdEvento(eventoParam);
        cargarMisSectores(eventoParam);
        const res = await requestJSON(`/eventos/${eventoParam}/entradas-no-validadas`);
        setPendientes(res.entradas || []);
      }
    } catch {}
  }

  async function cargarDispositivos() {
    const puedeValidar = roles.funcionario || roles.admin;
    if (!puedeValidar || !email) return;
    setDEmailFunc(email);
    try {
      const data = await requestJSON('/funcionario/' + encodeURIComponent(email) + '/dispositivos');
      const ds = data.dispositivos || [];
      setDispositivos(ds);
      setDispositivosReg(ds);
      if (ds.length === 1) {
        setVIdDispositivo(String(ds[0].idDispositivo));
        setUltimoDisp(ds[0].idDispositivo);
        setUltimoEmail(email);
      }
    } catch {}
  }

  async function cargarMisSectores(idEvento) {
    const esFunc = roles.funcionario && !roles.admin;
    if (!esFunc || !idEvento) { setSectoresBanner(''); return; }
    try {
      const data = await requestJSON(`/eventos/${idEvento}/mis-sectores`);
      const sectores = data.sectores || [];
      if (!sectores.length) { setSectoresBanner(''); return; }
      setSectoresBanner(sectores.map(s =>
        `<span style="background:var(--md-primary);color:#fff;padding:2px 10px;border-radius:999px;font-size:0.82rem;font-weight:600;">${s}</span>`
      ).join(' '));
    } catch { setSectoresBanner(''); }
  }

  async function cargarEntradasPendientes() {
    if (!leIdEvento) { alert('Seleccioná un evento primero'); return; }
    if (!ultimoDisp) { alert('Seleccioná un dispositivo primero'); return; }
    cargarMisSectores(leIdEvento);
    try {
      const data = await requestJSON(`/eventos/${leIdEvento}/entradas-no-validadas`);
      setPendientes(data.entradas || []);
    } catch {}
  }

  async function leerQRyValidar(idEntrada) {
    try {
      const res = await post('/entrada/' + idEntrada + '/qr', { tiempoVencimiento: 30 });
      await post('/validar', { idToken: res.idToken, idDispositivo: ultimoDisp, emailFuncionario: ultimoEmail });
      await cargarEntradasPendientes();
      setVaIdEvento(leIdEvento);
      cargarEntradasValidadas();
    } catch (err) { alert(err.message); }
  }

  async function cargarEntradasValidadas() {
    const idEvento = vaIdEvento;
    if (!idEvento) { alert('Seleccioná un evento primero'); return; }
    try {
      const data = await requestJSON(`/eventos/${idEvento}/entradas-validadas`);
      setValidadas(data.entradas || []);
    } catch {}
  }

  async function cargarCobertura() {
    if (!cobIdEvento) { alert('Seleccioná un evento primero'); return; }
    try {
      const data = await requestJSON(`/eventos/${cobIdEvento}/cobertura`);
      setCobertura(data.cobertura || []);
    } catch {}
  }

  async function registrarDispositivo() {
    try {
      const res = await post('/dispositivo', { dirMAC: dMac, alias: dAlias || null, emailFuncionario: dEmailFunc });
      setUltimoDisp(res.idDispositivo);
      setUltimoEmail(res.emailFuncionario);
      setVIdDispositivo(String(res.idDispositivo));
      setDAlias('');
      setResDisp('Dispositivo registrado correctamente. ID: ' + res.idDispositivo);
      const data = await requestJSON('/funcionario/' + encodeURIComponent(email) + '/dispositivos');
      setDispositivosReg(data.dispositivos || []);
    } catch (err) { setResDisp(err.message); }
  }

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Validación</p>
        <h1>Validación de entradas</h1>
        <p className="hero-copy">Seleccioná un evento, revisá las entradas pendientes y validalas con un dispositivo registrado.</p>
      </div>

      <div className="panel">
        <h2>1. Registrar dispositivo</h2>
        <div className="form-grid">
          <input placeholder="AA:BB:CC:DD:EE:FF" pattern="^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$" value={dMac} onChange={e => setDMac(e.target.value)} />
          <input placeholder="Alias (ej: Lector puerta A)" value={dAlias} onChange={e => setDAlias(e.target.value)} />
          <input placeholder="Email funcionario" value={dEmailFunc} onChange={e => setDEmailFunc(e.target.value)} />
        </div>
        <div className="actions"><button className="btn tonal" onClick={registrarDispositivo}><span className="material-symbols-outlined">devices</span> Registrar dispositivo</button></div>
        <div className="result">{resDisp}</div>
        <h3 style={{ margin: '16px 0 8px 0', fontSize: '0.9rem' }}>Dispositivos registrados</h3>
        <div className="result">
          {dispositivosReg.length === 0 ? <span className="small-note">No hay dispositivos registrados para este email.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>#</th><th>Alias</th><th>Dirección MAC</th></tr></thead>
                <tbody>
                  {dispositivosReg.map(d => (
                    <tr key={d.idDispositivo}><td>{d.idDispositivo}</td><td>{d.alias || '-'}</td><td>{d.dirMAC}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>2. Leer QR — entradas pendientes por evento</h2>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
          <select style={{ flex: 2, minWidth: '200px' }} value={leIdEvento} onChange={e => setLeIdEvento(e.target.value)}>
            <option value="">Seleccioná un evento</option>
            {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.nombreEvento} — {e.fecha}</option>)}
          </select>
          <select style={{ flex: 1, minWidth: '160px' }} value={vIdDispositivo} onChange={e => { setVIdDispositivo(e.target.value); if (e.target.value) { setUltimoDisp(parseInt(e.target.value)); setUltimoEmail(email); } }}>
            <option value="">Dispositivo...</option>
            {dispositivos.map(d => <option key={d.idDispositivo} value={d.idDispositivo}>{d.alias || '#' + d.idDispositivo} — {d.dirMAC}</option>)}
          </select>
          <button className="btn outlined" onClick={cargarEntradasPendientes}><span className="material-symbols-outlined">refresh</span> Cargar</button>
        </div>
        {sectoresBanner && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--md-primary)' }}>badge</span>
            <span style={{ fontSize: '0.88rem', color: 'var(--md-on-surface-variant)' }}>Tus sectores asignados:</span>
            <span dangerouslySetInnerHTML={{ __html: sectoresBanner }} />
          </div>
        )}
        <div className="result">
          {pendientes === null ? <span className="small-note">Seleccioná un evento, elegí un dispositivo y presioná "Cargar".</span> : pendientes.length === 0 ? <span className="small-note">No hay entradas pendientes de validación.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>ID</th><th>Propietario</th><th>Sector</th><th>Estado</th><th>Acción</th></tr></thead>
                <tbody>
                  {pendientes.map(e => (
                    <tr key={e.idEntrada}>
                      <td>#{e.idEntrada}</td><td>{e.emailPropietario}</td><td>{e.sectorCodigo}</td><td>{e.estado}</td>
                      <td><button className="btn" style={{ padding: '4px 12px', fontSize: '0.82rem' }} onClick={() => leerQRyValidar(e.idEntrada)}><span className="material-symbols-outlined" style={{ fontSize: '16px' }}>qr_code_scanner</span> Leer QR y validar</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>3. Validaciones realizadas</h2>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <select style={{ flex: 1 }} value={vaIdEvento} onChange={e => setVaIdEvento(e.target.value)}>
            <option value="">Seleccioná un evento</option>
            {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.nombreEvento} — {e.fecha}</option>)}
          </select>
          <button className="btn outlined" onClick={cargarEntradasValidadas}><span className="material-symbols-outlined">refresh</span> Cargar</button>
        </div>
        <div className="result">
          {validadas === null ? <span className="small-note">Seleccioná un evento y presioná "Cargar".</span> : validadas.length === 0 ? <span className="small-note">No hay validaciones realizadas.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>ID</th><th>Propietario</th><th>Sector</th><th>Funcionario</th><th>Dispositivo</th><th>Fecha/Hora</th></tr></thead>
                <tbody>
                  {validadas.map(e => (
                    <tr key={e.idEntrada}>
                      <td>#{e.idEntrada}</td><td>{e.emailPropietario}</td><td>{e.sectorCodigo}</td>
                      <td>{e.emailFuncionario}</td><td>{e.dirMAC}</td><td>{e.fechaHoraValidacion}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>4. Cobertura de funcionarios por evento</h2>
        <p className="small-note" style={{ marginBottom: '12px' }}>Cada funcionario debe validar al menos una entrada en cada sector que le fue asignado.</p>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <select style={{ flex: 1 }} value={cobIdEvento} onChange={e => setCobIdEvento(e.target.value)}>
            <option value="">Seleccioná un evento</option>
            {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.nombreEvento} — {e.fecha}</option>)}
          </select>
          <button className="btn outlined" onClick={cargarCobertura}><span className="material-symbols-outlined">verified_user</span> Ver cobertura</button>
        </div>
        <div className="result">
          {cobertura === null ? <span className="small-note">Seleccioná un evento y presioná "Ver cobertura".</span> : cobertura.length === 0 ? <span className="small-note">No hay funcionarios asignados a este evento.</span> : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead><tr><th>Funcionario</th><th>Sectores asignados</th><th>Progreso de escaneo</th><th>Cobertura</th></tr></thead>
                <tbody>
                  {cobertura.map(f => (
                    <tr key={f.emailFuncionario}>
                      <td>{f.emailFuncionario}</td>
                      <td>{f.sectores.map(s => (
                        <span key={s.sectorCodigo} style={{ marginRight: '10px', color: s.cumple ? '#1a7a4a' : '#c0392b' }}>
                          {s.cumple ? '\u2713' : '\u26A0'} Sector {s.sectorCodigo}
                        </span>
                      ))}</td>
                      <td>{f.sectores.map(s => (
                        <span key={s.sectorCodigo} style={{ marginRight: '6px', background: s.faltantes === 0 ? '#d1fae5' : '#fef3c7', color: s.faltantes === 0 ? '#1a7a4a' : '#b45309', padding: '2px 8px', borderRadius: '999px', fontSize: '0.78rem', fontWeight: 600 }}>
                          Sector {s.sectorCodigo}: {s.validaciones}/{s.totalEntradas}{s.faltantes > 0 ? ` — faltan ${s.faltantes}` : ''}
                        </span>
                      ))}</td>
                      <td>{f.cobertura_completa
                        ? <span style={{ color: '#1a7a4a', fontWeight: 600 }}>&#10003; Completa</span>
                        : <span style={{ color: '#c0392b', fontWeight: 600 }}>&#9888; Incompleta</span>
                      }</td>
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
