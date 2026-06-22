import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post } from '../api.js';

export default function Infraestructura() {
  const { session } = useOutletContext();
  const email = session?.email;

  const HDR = ['idEstadio','nombre','pais','ciudad','emailAdmin','fechaAsignacion','idSector','estadio','codigo','capacidadMaxima','costoEntrada','idEvento','nombreEvento','fecha','hora','equipos','tipo','idReferencia','referencia','detalle'];

  function sortHeaders(headers) {
    const rank = (h) => { const p = HDR.indexOf(h); return p === -1 ? 999 : p; };
    return [...headers].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
  }

  function renderTable(rows, columns) {
    if (!rows || !rows.length) return '<div class="small-note">No hay datos cargados todavía.</div>';
    const cols = columns ? columns.map(c => typeof c === 'string' ? { key: c, label: c } : c) : sortHeaders(Object.keys(rows[0])).map(k => ({ key: k, label: k }));
    const head = cols.map(c => `<th>${c.label}</th>`).join('');
    const body = rows.map(row => `<tr>${cols.map(c => `<td>${row[c.key] ?? ''}</td>`).join('')}</tr>`).join('');
    return `<div style="overflow-x:auto;"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
  }

  // States
  const [estNombre, setEstNombre] = useState('');
  const [estPais, setEstPais] = useState('');
  const [estCiudad, setEstCiudad] = useState('');
  const [estFecha, setEstFecha] = useState('');
  const [resEstadio, setResEstadio] = useState('');
  const [resEstadios, setResEstadios] = useState('');

  const [secIdEstadio, setSecIdEstadio] = useState('');
  const [secCodigo, setSecCodigo] = useState('');
  const [secCapacidad, setSecCapacidad] = useState('');
  const [secCosto, setSecCosto] = useState('');
  const [resSector, setResSector] = useState('');
  const [resSectores, setResSectores] = useState('');

  const [evNombre, setEvNombre] = useState('');
  const [evFecha, setEvFecha] = useState('');
  const [evHora, setEvHora] = useState('');
  const [evIdEstadio, setEvIdEstadio] = useState('');
  const [resEvento, setResEvento] = useState('');
  const [resEventos, setResEventos] = useState('');

  const [eeIdEvento, setEeIdEvento] = useState('');
  const [eeIdEquipo, setEeIdEquipo] = useState('');
  const [eeRol, setEeRol] = useState('');
  const [resVinculos, setResVinculos] = useState('');
  const [resVinculaciones, setResVinculaciones] = useState('');

  const [esIdEvento, setEsIdEvento] = useState('');
  const [esIdSector, setEsIdSector] = useState('');
  const [resHabSector, setResHabSector] = useState('');
  const [resSectHab, setResSectHab] = useState('');

  const [afIdEvento, setAfIdEvento] = useState('');
  const [afIdSector, setAfIdSector] = useState('');
  const [afEmailFunc, setAfEmailFunc] = useState('');
  const [resAsigFunc, setResAsigFunc] = useState('');
  const [resAsignaciones, setResAsignaciones] = useState('');

  const [estadios, setEstadios] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [funcionarios, setFuncionarios] = useState([]);

  useEffect(() => { cargarEventos(); cargarEstadios(); cargarSectores(); cargarVinculaciones(); }, []);
  useEffect(() => { if (session?.roles?.admin) { cargarCodigosDisponibles(); cargarEquiposDisponibles(); cargarSectoresDisponiblesEvento(); cargarFuncionarios(); cargarSectoresEventoAF(); } }, [estadios, eventos]);

  async function cargarEventos() {
    try {
      const data = await requestJSON('/eventos');
      setEventos(data.eventos || []);
      setResEventos(renderTable(data.eventos, [
        { key: 'nombreEvento', label: 'Evento' }, { key: 'fecha', label: 'Fecha' }, { key: 'hora', label: 'Hora' },
        { key: 'estadio', label: 'Estadio' }, { key: 'paisEstadio', label: 'País' }, { key: 'ciudadEstadio', label: 'Ciudad' }, { key: 'equipos', label: 'Equipos' },
      ]));
    } catch {}
  }

  async function cargarEstadios() {
    try {
      const data = await requestJSON('/estadios');
      const list = data.estadios || [];
      setEstadios(list);
      setResEstadios(renderTable(list, [
        { key: 'nombre', label: 'Nombre' }, { key: 'pais', label: 'País' }, { key: 'ciudad', label: 'Ciudad' },
        { key: 'emailAdmin', label: 'Admin' }, { key: 'fechaAsignacion', label: 'Asignación' },
      ]));
      if (list.length) {
        if (!secIdEstadio) setSecIdEstadio(String(list[0].idEstadio));
        if (!evIdEstadio) setEvIdEstadio(String(list[0].idEstadio));
      }
    } catch {}
  }

  async function cargarSectores() {
    try {
      const data = await requestJSON('/sectores');
      const sectores = data.sectores || [];
      if (!sectores.length) { setResSectores('<span class="small-note">No hay sectores.</span>'); return; }
      setResSectores('<div style="overflow-x:auto;"><table><thead><tr><th>Código</th><th>Estadio</th><th>Capacidad</th><th>Costo</th><th>Acción</th></tr></thead><tbody>' +
        sectores.map(s => `<tr><td>${s.codigo}</td><td>${s.estadio}</td><td>${s.capacidadMaxima}</td><td>$${s.costoEntrada}</td>
          <td><button class="btn outlined" style="padding:4px 12px;font-size:0.82rem;" onclick="window.eliminarSector(${s.idSector},'${s.codigo}','${s.estadio}')"><span class="material-symbols-outlined" style="font-size:16px;">delete</span> Eliminar</button></td>
        </tr>`).join('') + '</tbody></table></div>');
    } catch {}
  }

  async function cargarVinculaciones() {
    try {
      const data = await requestJSON('/vinculaciones');
      setResVinculaciones(renderTable(data.vinculaciones, [
        { key: 'tipo', label: 'Tipo' }, { key: 'nombreEvento', label: 'Evento' }, { key: 'referencia', label: 'Referencia' }, { key: 'detalle', label: 'Detalle' },
      ]));
    } catch {}
  }

  async function cargarCodigosDisponibles() {
    if (!secIdEstadio) return;
    try {
      const data = await requestJSON(`/estadios/${secIdEstadio}/codigos-disponibles`);
      const codigos = data.codigos || [];
      if (codigos.length && !secCodigo) setSecCodigo(codigos[0].codigo);
    } catch {}
  }

  async function cargarEquiposDisponibles() {
    if (!eeIdEvento) return;
    try {
      const data = await requestJSON(`/eventos/${eeIdEvento}/equipos-disponibles`);
      const equipos = data.equipos || [];
      if (equipos.length && !eeIdEquipo) setEeIdEquipo(String(equipos[0].idEquipo));
    } catch {}
  }

  async function cargarSectoresDisponiblesEvento() {
    if (!esIdEvento) return;
    try {
      const data = await requestJSON(`/eventos/${esIdEvento}/sectores-disponibles`);
      const sectores = data.sectores || [];
      if (sectores.length && !esIdSector) setEsIdSector(String(sectores[0].idSector));
    } catch {}
  }

  async function cargarSectoresEventoAF() {
    if (!afIdEvento) { return; }
    try {
      const data = await requestJSON(`/eventos/${afIdEvento}/sectores`);
      const sectores = data.sectores || [];
      if (sectores.length && !afIdSector) setAfIdSector(String(sectores[0].idSector));
    } catch {}
  }

  async function cargarFuncionarios() {
    try {
      const data = await requestJSON('/funcionarios');
      setFuncionarios(data.funcionarios || []);
    } catch {}
  }

  // Handlers
  async function crearEstadio() {
    try {
      const r = await post('/estadio', { nombre: estNombre, pais: estPais, ciudad: estCiudad, emailAdmin: email, fechaAsignacion: estFecha });
      setResEstadio('Estadio creado correctamente. ID: ' + r.idEstadio);
      cargarEstadios();
    } catch (err) { setResEstadio(err.message); }
  }

  async function crearSector() {
    try {
      const r = await post('/sector', { idEstadio: secIdEstadio, codigo: secCodigo, capacidadMaxima: secCapacidad, costoEntrada: secCosto });
      setResSector('Sector creado correctamente. ID: ' + r.idSector);
      cargarEstadios(); cargarSectores();
    } catch (err) { setResSector(err.message); }
  }

  async function crearEvento() {
    try {
      const r = await post('/evento', { nombreEvento: evNombre, fecha: evFecha, hora: evHora, idEstadio: evIdEstadio, emailAdmin: email });
      setResEvento('Evento creado correctamente. ID: ' + r.idEvento);
      cargarEventos();
    } catch (err) { setResEvento(err.message); }
  }

  async function vincularEquipo() {
    try {
      await post('/evento/equipo', { idEvento: eeIdEvento, idEquipo: eeIdEquipo, rol: eeRol });
      setResVinculos('&#10003; Equipo vinculado correctamente');
      cargarEventos();
      cargarEquiposDisponibles();
    } catch (err) { setResVinculos(err.message); }
  }

  async function habilitarSector() {
    try {
      await post('/evento/sector', { idEvento: esIdEvento, idSector: esIdSector });
      setResHabSector('Sector habilitado correctamente');
      cargarEventos();
      cargarSectoresDisponiblesEvento();
      cargarSectoresHabilitados();
      if (afIdEvento) cargarSectoresEventoAF();
    } catch (err) { setResHabSector(err.message); }
  }

  async function cargarSectoresHabilitados() {
    if (!esIdEvento) { setResSectHab(''); return; }
    try {
      const data = await requestJSON(`/eventos/${esIdEvento}/sectores`);
      const sectores = data.sectores || [];
      if (!sectores.length) { setResSectHab('<span class="small-note">No hay sectores habilitados.</span>'); return; }
      setResSectHab('<div style="overflow-x:auto;"><table><thead><tr><th>Sector</th><th>Capacidad</th><th>Costo</th><th>Vendidas</th><th>Disponibles</th><th>Acción</th></tr></thead><tbody>' +
        sectores.map(s => `<tr><td>${s.codigo}</td><td>${s.capacidadMaxima}</td><td>$${s.costoEntrada}</td><td>${s.entradasVendidas}</td><td>${s.entradasDisponibles}</td>
          <td><button class="btn outlined" style="padding:4px 12px;font-size:0.82rem;" onclick="if(confirm('Deshabilitar?')){fetch('/evento/sector',{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({idEvento:${esIdEvento},idSector:${s.idSector}})}).then(r=>location.reload())}"><span class="material-symbols-outlined" style="font-size:16px;">remove_circle</span> Deshabilitar</button></td>
        </tr>`).join('') + '</tbody></table></div>');
    } catch {}
  }

  async function asignarFuncionarioSector() {
    try {
      await post('/asignacion', { idEvento: parseInt(afIdEvento), idSector: parseInt(afIdSector), emailFuncionario: afEmailFunc });
      setResAsigFunc('Funcionario asignado correctamente');
      cargarAsignaciones();
    } catch (err) { setResAsigFunc(err.message); }
  }

  async function cargarAsignaciones() {
    if (!afIdEvento) { setResAsignaciones('<span class="small-note">Selecciona un evento primero</span>'); return; }
    try {
      const data = await requestJSON(`/eventos/${afIdEvento}/asignaciones`);
      const rows = data.asignaciones || [];
      if (!rows.length) { setResAsignaciones('<span class="small-note">No hay asignaciones.</span>'); return; }
      setResAsignaciones('<div style="overflow-x:auto;"><table><thead><tr><th>Sector</th><th>Email</th><th>Documento</th><th>Acción</th></tr></thead><tbody>' +
        rows.map(r => `<tr><td>${r.sectorCodigo}</td><td>${r.emailFuncionario}</td><td>${r.docPais}-${r.docTipo} ${r.docNumero}</td>
          <td><button class="btn outlined" style="padding:6px 16px;font-size:0.82rem;" onclick="if(confirm('Eliminar?')){fetch('/asignacion',{method:'DELETE',headers:{'Content-Type':'application/json'},body:JSON.stringify({idEvento:${r.idEvento},idSector:${r.idSector},emailFuncionario:'${r.emailFuncionario}'})}).then(r=>location.reload())}"><span class="material-symbols-outlined" style="font-size:16px;">delete</span> Eliminar</button></td>
        </tr>`).join('') + '</tbody></table></div>');
    } catch {}
  }

  // Make eliminarSector available to window for onclick inline handlers
  useEffect(() => {
    window.eliminarSector = async (idSector, codigo, estadio) => {
      if (!confirm(`Eliminar sector ${codigo} de ${estadio}?`)) return;
      try {
        await requestJSON(`/sector/${idSector}`, { method: 'DELETE' });
        setResSector(`Sector ${codigo} eliminado correctamente`);
        cargarSectores();
      } catch (err) { setResSector(err.message); }
    };
    return () => { delete window.eliminarSector; };
  }, []);

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Infraestructura</p>
        <h1>Estadios, sectores y eventos</h1>
        <p className="hero-copy">Aquí se administran los recintos, la capacidad por sector, los eventos y la relación con los equipos.</p>
        <p className="small-note">Las acciones de alta requieren un usuario administrador autenticado.</p>
        <p className="small-note">Usuario activo: <strong>{email || 'sin sesión'}</strong></p>
      </div>

      <div className="panel">
        <h2>Crear estadio</h2>
        <div className="form-grid">
          <input placeholder="Estadio" value={estNombre} onChange={e => setEstNombre(e.target.value)} />
          <input placeholder="País" value={estPais} onChange={e => setEstPais(e.target.value)} />
          <input placeholder="Ciudad" value={estCiudad} onChange={e => setEstCiudad(e.target.value)} />
          <input type="date" className="full" value={estFecha} onChange={e => setEstFecha(e.target.value)} />
        </div>
        <div className="actions">
          <button className="btn" onClick={crearEstadio}><span className="material-symbols-outlined">add_business</span> Crear estadio</button>
          <button className="btn outlined" onClick={cargarEstadios}><span className="material-symbols-outlined">visibility</span> Ver estadios</button>
        </div>
        <div className="result">{resEstadio}</div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resEstadios }} />
      </div>

      <div className="panel">
        <h2>Crear sector</h2>
        <div className="form-grid">
          <select value={secIdEstadio} onChange={e => { setSecIdEstadio(e.target.value); }}>
            <option value="">Selecciona un estadio</option>
            {estadios.map(e => <option key={e.idEstadio} value={e.idEstadio}>{e.idEstadio} | {e.nombre}</option>)}
          </select>
          <select value={secCodigo} onChange={e => setSecCodigo(e.target.value)}>
            <option value="">Selecciona un código</option>
          </select>
          <input placeholder="Capacidad" value={secCapacidad} onChange={e => setSecCapacidad(e.target.value)} />
          <input placeholder="Costo entrada" value={secCosto} onChange={e => setSecCosto(e.target.value)} />
        </div>
        <div className="actions">
          <button className="btn tonal" onClick={crearSector}><span className="material-symbols-outlined">select_all</span> Crear sector</button>
          <button className="btn outlined" onClick={cargarSectores}><span className="material-symbols-outlined">visibility</span> Ver sectores</button>
        </div>
        <div className="result">{resSector}</div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resSectores }} />
      </div>

      <div className="panel">
        <h2>Crear evento</h2>
        <div className="form-grid">
          <input placeholder="Nombre evento" value={evNombre} onChange={e => setEvNombre(e.target.value)} />
          <input type="date" value={evFecha} onChange={e => setEvFecha(e.target.value)} />
          <input type="time" step="1" value={evHora} onChange={e => setEvHora(e.target.value)} />
          <select value={evIdEstadio} onChange={e => setEvIdEstadio(e.target.value)}>
            <option value="">Selecciona un estadio</option>
            {estadios.map(e => <option key={e.idEstadio} value={e.idEstadio}>{e.idEstadio} | {e.nombre}</option>)}
          </select>
        </div>
        <div className="actions">
          <button className="btn" onClick={crearEvento}><span className="material-symbols-outlined">event</span> Crear evento</button>
          <button className="btn outlined" onClick={cargarEventos}><span className="material-symbols-outlined">visibility</span> Ver eventos</button>
        </div>
        <div className="result">{resEvento}</div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resEventos }} />
      </div>

      <div className="panel">
        <h2>Vincular equipo a evento</h2>
        <p className="small-note">Asigna un equipo como <strong>local</strong> o <strong>visitante</strong> a un evento existente.</p>
        <div className="form-grid">
          <div>
            <label className="field-label">Evento</label>
            <select value={eeIdEvento} onChange={e => { setEeIdEvento(e.target.value); }}>
              <option value="">Selecciona un evento</option>
              {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.idEvento} | {e.nombreEvento}</option>)}
            </select>
          </div>
          <div>
            <label className="field-label">Equipo</label>
            <select value={eeIdEquipo} onChange={e => setEeIdEquipo(e.target.value)}>
              <option value="">Selecciona un evento primero</option>
            </select>
          </div>
          <div>
            <label className="field-label">Rol</label>
            <select value={eeRol} onChange={e => setEeRol(e.target.value)}>
              <option value="">Selecciona un rol</option>
              <option value="local">Local</option>
              <option value="visitante">Visitante</option>
            </select>
          </div>
        </div>
        <div className="actions">
          <button className="btn tonal" onClick={vincularEquipo}><span className="material-symbols-outlined">group_add</span> Vincular equipo</button>
          <button className="btn outlined" onClick={cargarVinculaciones}><span className="material-symbols-outlined">link</span> Ver vinculaciones</button>
        </div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resVinculos }} />
        <div className="result" dangerouslySetInnerHTML={{ __html: resVinculaciones }} />
      </div>

      <div className="panel">
        <h2>Habilitar / Deshabilitar sector en evento</h2>
        <p className="small-note">Vincula o desvincula un sector del estadio a un evento.</p>
        <div className="form-grid">
          <div>
            <label className="field-label">Evento</label>
            <select value={esIdEvento} onChange={e => { setEsIdEvento(e.target.value); cargarSectoresHabilitados(); }}>
              <option value="">Selecciona un evento</option>
              {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.idEvento} | {e.nombreEvento}</option>)}
            </select>
          </div>
          <div>
            <label className="field-label">Sector a habilitar</label>
            <select value={esIdSector} onChange={e => setEsIdSector(e.target.value)}>
              <option value="">Selecciona un evento primero</option>
            </select>
          </div>
        </div>
        <div className="actions">
          <button className="btn tonal" onClick={habilitarSector}><span className="material-symbols-outlined">check_circle</span> Habilitar sector</button>
        </div>
        <div className="result">{resHabSector}</div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resSectHab }} />
      </div>

      <div className="panel">
        <h2>Asignación de funcionarios</h2>
        <div className="form-grid">
          <select value={afIdEvento} onChange={e => { setAfIdEvento(e.target.value); }}>
            <option value="">Selecciona un evento</option>
            {eventos.map(e => <option key={e.idEvento} value={e.idEvento}>{e.idEvento} | {e.nombreEvento}</option>)}
          </select>
          <select value={afIdSector} onChange={e => setAfIdSector(e.target.value)}>
            <option value="">Selecciona un evento primero</option>
          </select>
          <select value={afEmailFunc} onChange={e => setAfEmailFunc(e.target.value)}>
            <option value="">Selecciona funcionario</option>
            {funcionarios.map(f => <option key={f.email} value={f.email}>{f.email} | Legajo {f.numeroLegajo}</option>)}
          </select>
        </div>
        <div className="actions">
          <button className="btn tonal" onClick={asignarFuncionarioSector}><span className="material-symbols-outlined">assignment_ind</span> Asignar funcionario</button>
          <button className="btn outlined" onClick={cargarAsignaciones}><span className="material-symbols-outlined">visibility</span> Ver asignaciones</button>
        </div>
        <div className="result">{resAsigFunc}</div>
        <div className="result" dangerouslySetInnerHTML={{ __html: resAsignaciones }} />
      </div>
    </section>
  );
}
