import { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { requestJSON, post, renderJson } from '../api.js';

const PAISES = [
  "Uruguay","Argentina","Brasil","Chile","Paraguay","Bolivia","Colombia","Ecuador","Perú","Venezuela",
  "México","USA","Canadá","Costa Rica","Honduras","Guatemala","El Salvador","Nicaragua","Panamá","Cuba",
  "República Dominicana","Haití","Jamaica","Trinidad y Tobago","Barbados","Bahamas",
  "Alemania","Francia","España","Italia","Portugal","Inglaterra","Países Bajos","Bélgica","Suiza","Austria",
  "Polonia","Croacia","Serbia","Eslovenia","Eslovaquia","República Checa","Hungría","Rumanía","Bulgaria","Grecia",
  "Suecia","Noruega","Dinamarca","Finlandia","Islandia","Irlanda","Escocia","Gales",
  "Rusia","Ucrania","Turquía","Georgia","Armenia","Azerbaiyán",
  "Marruecos","Senegal","Nigeria","Camerún","Ghana","Costa de Marfil","Túnez","Argelia","Egipto","Sudáfrica",
  "Japón","Corea del Sur","Arabia Saudita","Irán","Qatar","Australia","Nueva Zelanda",
  "China","India","Indonesia","Filipinas","Tailandia","Vietnam","Malasia",
  "Albania","Andorra","Bosnia y Herzegovina","Bielorrusia","Estonia","Letonia","Lituania","Luxemburgo",
  "Malta","Moldavia","Montenegro","Macedonia del Norte","San Marino","Kosovo"
].sort((a, b) => a.localeCompare(b, 'es'));

export default function Registro() {
  const { session } = useOutletContext();
  const [usuarioActual, setUsuarioActual] = useState(null);
  const [pendientes, setPendientes] = useState(null);

  // General
  const [gen, setGen] = useState({ email: '', passw: '', docPais: '', docTipo: '', docNumero: '', dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', telefonos: '' });
  // Admin
  const [adm, setAdm] = useState({ email: '', passw: '', docPais: '', docTipo: '', docNumero: '', dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', paisJurisdiccion: '', fechaAsignacionCargo: '' });
  // Funcionario
  const [fun, setFun] = useState({ email: '', passw: '', docPais: '', docTipo: '', docNumero: '', dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', numeroLegajo: '' });
  // Search
  const [sEmail, setSEmail] = useState('');
  const [formAct, setFormAct] = useState({ docPais: '', docTipo: '', docNumero: '', dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', telefonos: '' });
  const [searchResult, setSearchResult] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [rolAdmin, setRolAdmin] = useState(false);
  const [rolFunc, setRolFunc] = useState(false);
  const [resRoles, setResRoles] = useState('');
  const [resAct, setResAct] = useState('');

  const setters = { gen: setGen, adm: setAdm, fun: setFun };
  const s = (obj, field) => (e) => {
    const key = obj === gen ? 'gen' : obj === adm ? 'adm' : 'fun';
    setters[key]({ ...obj, [field]: e.target.value });
  };

  useEffect(() => { cargarPendientes(); }, []);

  async function registrarGeneral() {
    try {
      const res = await post('/registrar/general', gen);
      document.getElementById('resGeneral').innerHTML = renderJson(res);
    } catch (err) {
      document.getElementById('resGeneral').innerHTML = err.message;
    }
  }

  async function registrarAdmin() {
    try {
      const res = await post('/registrar/admin', adm);
      document.getElementById('resAdmin').innerHTML = renderJson(res);
    } catch (err) {
      document.getElementById('resAdmin').innerHTML = err.message;
    }
  }

  async function registrarFuncionario() {
    try {
      const res = await post('/registrar/funcionario', fun);
      document.getElementById('resFuncionario').innerHTML = renderJson(res);
    } catch (err) {
      document.getElementById('resFuncionario').innerHTML = err.message;
    }
  }

  async function buscarUsuario() {
    if (!sEmail) { alert('Ingresá un email'); return; }
    try {
      const data = await requestJSON('/usuario/' + encodeURIComponent(sEmail) + '/datos');
      setUsuarioActual(data);
      setSearchResult('<div class="pill" style="margin-bottom:12px;">Usuario encontrado: <strong>' + data.email + '</strong></div>');
      setFormAct({
        docPais: data.docPais || '',
        docTipo: data.docTipo || '',
        docNumero: data.docNumero || '',
        dirPais: data.dirPais || '',
        dirLocalidad: data.dirLocalidad || '',
        dirCalle: data.dirCalle || '',
        dirNumero: data.dirNumero || '',
        dirCodigoPostal: data.dirCodigoPostal || '',
        telefonos: (data.telefonos || []).join(', '),
      });
      setRolAdmin(data.esAdmin);
      setRolFunc(data.esFuncionario);
      setShowForm(true);
    } catch (err) {
      setSearchResult('<span class="small-note">' + err.message + '</span>');
      setShowForm(false);
      setUsuarioActual(null);
    }
  }

  async function guardarUsuario() {
    if (!usuarioActual) return;
    try {
      const payload = {
        docPais: formAct.docPais,
        docTipo: formAct.docTipo,
        docNumero: formAct.docNumero,
        dirPais: formAct.dirPais,
        dirLocalidad: formAct.dirLocalidad,
        dirCalle: formAct.dirCalle,
        dirNumero: formAct.dirNumero,
        dirCodigoPostal: formAct.dirCodigoPostal,
        telefonos: formAct.telefonos.split(',').map(t => t.trim()).filter(Boolean),
      };
      await requestJSON('/usuario/' + encodeURIComponent(usuarioActual.email) + '/datos', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      setResAct('Datos actualizados correctamente');
    } catch (err) {
      setResAct(err.message);
    }
  }

  async function cambiarRol(rol) {
    if (!usuarioActual) return;
    const checked = rol === 'admin' ? rolAdmin : rolFunc;
    const accion = checked ? 'agregar' : 'quitar';
    try {
      const payload = { accion, rol };
      if (rol === 'admin' && accion === 'agregar') {
        payload.paisJurisdiccion = prompt('País de jurisdicción para el admin:') || '';
        payload.fechaAsignacionCargo = prompt('Fecha de asignación (YYYY-MM-DD):') || '';
      }
      if (rol === 'funcionario' && accion === 'agregar') {
        payload.numeroLegajo = prompt('Número de legajo (dejá vacío para auto-generar):') || '';
      }
      await requestJSON('/usuario/' + encodeURIComponent(usuarioActual.email) + '/roles', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      setResRoles('Rol ' + (accion === 'agregar' ? 'agregado' : 'quitado') + ' correctamente');
    } catch (err) {
      if (rol === 'admin') setRolAdmin(!checked);
      if (rol === 'funcionario') setRolFunc(!checked);
      setResRoles(err.message);
    }
  }

  async function verificarUsuario(email, estado) {
    try {
      await post('/usuarios/' + email + '/verificar', { estado });
      cargarPendientes();
    } catch (err) {
      alert(err.message);
    }
  }

  async function cargarPendientes() {
    try {
      const data = await requestJSON('/usuarios/pendientes');
      setPendientes(data.pendientes || []);
    } catch {
      setPendientes([]);
    }
  }

  const selStyle = { appearance: 'auto' };

  return (
    <section className="page-grid">
      <div className="hero-card" style={{ gridColumn: '1 / -1' }}>
        <p className="eyebrow">Registro</p>
        <h1>Usuarios del sistema</h1>
        <p className="hero-copy">Creá nuevos usuarios con rol específico, administrá pendientes de validación y actualizá datos de usuarios existentes.</p>
      </div>

      <div className="panel">
        <h2>Usuario general</h2>
        <div className="form-grid">
          <input placeholder="Email" value={gen.email} onChange={s(gen, 'email')} />
          <input placeholder="Contraseña" type="password" value={gen.passw} onChange={s(gen, 'passw')} />
          <select style={selStyle} value={gen.docPais} onChange={s(gen, 'docPais')}><option value="">País doc</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <select style={selStyle} value={gen.docTipo} onChange={s(gen, 'docTipo')}>
            <option value="">Tipo doc</option>
            <option value="CI">CI</option>
            <option value="DNI">DNI</option>
            <option value="PAS">Pasaporte</option>
            <option value="SSN">SSN</option>
          </select>
          <input placeholder="Número doc" value={gen.docNumero} onChange={s(gen, 'docNumero')} />
          <select style={selStyle} value={gen.dirPais} onChange={s(gen, 'dirPais')}><option value="">País dirección</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <input placeholder="Localidad" value={gen.dirLocalidad} onChange={s(gen, 'dirLocalidad')} />
          <input placeholder="Calle" value={gen.dirCalle} onChange={s(gen, 'dirCalle')} />
          <input placeholder="Número" value={gen.dirNumero} onChange={s(gen, 'dirNumero')} />
          <input placeholder="Código postal" value={gen.dirCodigoPostal} onChange={s(gen, 'dirCodigoPostal')} />
          <input placeholder="Teléfonos separados por coma" className="full" value={gen.telefonos} onChange={s(gen, 'telefonos')} />
        </div>
        <div className="actions"><button className="btn" onClick={registrarGeneral}><span className="material-symbols-outlined">person_add</span> Registrar general</button></div>
        <div className="result" id="resGeneral"></div>
      </div>

      <div className="panel">
        <h2>Administrador</h2>
        <div className="form-grid">
          <input placeholder="Email" value={adm.email} onChange={s(adm, 'email')} />
          <input placeholder="Contraseña" type="password" value={adm.passw} onChange={s(adm, 'passw')} />
          <select style={selStyle} value={adm.docPais} onChange={s(adm, 'docPais')}><option value="">País doc</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <select style={selStyle} value={adm.docTipo} onChange={s(adm, 'docTipo')}>
            <option value="">Tipo doc</option>
            <option value="CI">CI</option><option value="DNI">DNI</option><option value="PAS">Pasaporte</option>
            <option value="LC">Licencia de Conducir</option><option value="RES">Doc. de Residencia</option>
          </select>
          <input placeholder="Número doc" value={adm.docNumero} onChange={s(adm, 'docNumero')} />
          <select style={selStyle} value={adm.dirPais} onChange={s(adm, 'dirPais')}><option value="">País dirección</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <input placeholder="Localidad" value={adm.dirLocalidad} onChange={s(adm, 'dirLocalidad')} />
          <input placeholder="Calle" value={adm.dirCalle} onChange={s(adm, 'dirCalle')} />
          <input placeholder="Número" value={adm.dirNumero} onChange={s(adm, 'dirNumero')} />
          <input placeholder="Código postal" value={adm.dirCodigoPostal} onChange={s(adm, 'dirCodigoPostal')} />
          <select style={selStyle} value={adm.paisJurisdiccion} onChange={s(adm, 'paisJurisdiccion')}><option value="">País jurisdicción</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <input type="date" value={adm.fechaAsignacionCargo} onChange={s(adm, 'fechaAsignacionCargo')} />
        </div>
        <div className="actions"><button className="btn tonal" onClick={registrarAdmin}><span className="material-symbols-outlined">admin_panel_settings</span> Registrar administrador</button></div>
        <div className="result" id="resAdmin"></div>
      </div>

      <div className="panel">
        <h2>Funcionario</h2>
        <div className="form-grid">
          <input placeholder="Email" value={fun.email} onChange={s(fun, 'email')} />
          <input placeholder="Contraseña" type="password" value={fun.passw} onChange={s(fun, 'passw')} />
          <select style={selStyle} value={fun.docPais} onChange={s(fun, 'docPais')}><option value="">País doc</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <select style={selStyle} value={fun.docTipo} onChange={s(fun, 'docTipo')}>
            <option value="">Tipo doc</option>
            <option value="CI">CI</option><option value="DNI">DNI</option><option value="PAS">Pasaporte</option>
            <option value="LC">Licencia de Conducir</option><option value="RES">Doc. de Residencia</option>
          </select>
          <input placeholder="Número doc" value={fun.docNumero} onChange={s(fun, 'docNumero')} />
          <select style={selStyle} value={fun.dirPais} onChange={s(fun, 'dirPais')}><option value="">País dirección</option>{PAISES.map(p => <option key={p} value={p}>{p}</option>)}</select>
          <input placeholder="Localidad" value={fun.dirLocalidad} onChange={s(fun, 'dirLocalidad')} />
          <input placeholder="Calle" value={fun.dirCalle} onChange={s(fun, 'dirCalle')} />
          <input placeholder="Número" value={fun.dirNumero} onChange={s(fun, 'dirNumero')} />
          <input placeholder="Código postal" value={fun.dirCodigoPostal} onChange={s(fun, 'dirCodigoPostal')} />
          <input placeholder="Número de legajo" className="full" value={fun.numeroLegajo} onChange={s(fun, 'numeroLegajo')} />
        </div>
        <div className="actions"><button className="btn tonal" onClick={registrarFuncionario}><span className="material-symbols-outlined">badge</span> Registrar funcionario</button></div>
        <div className="result" id="resFuncionario"></div>
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>Buscar y actualizar usuario</h2>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <input placeholder="Email del usuario a buscar" style={{ flex: 1 }} value={sEmail} onChange={e => setSEmail(e.target.value)} />
          <button className="btn outlined" onClick={buscarUsuario}><span className="material-symbols-outlined">search</span> Buscar</button>
        </div>
        <div className="result" dangerouslySetInnerHTML={{ __html: searchResult }} />
        {showForm && (
          <div id="formActualizar">
            <div className="form-grid" style={{ marginTop: '16px' }}>
              <input placeholder="País doc" value={formAct.docPais} onChange={e => setFormAct(f => ({ ...f, docPais: e.target.value }))} />
              <input placeholder="Tipo doc" value={formAct.docTipo} onChange={e => setFormAct(f => ({ ...f, docTipo: e.target.value }))} />
              <input placeholder="Número doc" value={formAct.docNumero} onChange={e => setFormAct(f => ({ ...f, docNumero: e.target.value }))} />
              <input placeholder="País dirección" value={formAct.dirPais} onChange={e => setFormAct(f => ({ ...f, dirPais: e.target.value }))} />
              <input placeholder="Localidad" value={formAct.dirLocalidad} onChange={e => setFormAct(f => ({ ...f, dirLocalidad: e.target.value }))} />
              <input placeholder="Calle" value={formAct.dirCalle} onChange={e => setFormAct(f => ({ ...f, dirCalle: e.target.value }))} />
              <input placeholder="Número" value={formAct.dirNumero} onChange={e => setFormAct(f => ({ ...f, dirNumero: e.target.value }))} />
              <input placeholder="Código postal" value={formAct.dirCodigoPostal} onChange={e => setFormAct(f => ({ ...f, dirCodigoPostal: e.target.value }))} />
              <input placeholder="Teléfonos separados por coma" className="full" value={formAct.telefonos} onChange={e => setFormAct(f => ({ ...f, telefonos: e.target.value }))} />
            </div>
            <div className="actions" style={{ marginTop: '12px' }}>
              <button className="btn tonal" onClick={guardarUsuario}><span className="material-symbols-outlined">save</span> Guardar cambios</button>
            </div>
            <div className="result">{resAct}</div>
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--md-outline-variant)' }}>
              <p className="small-note" style={{ marginBottom: '8px' }}>Administrar permisos:</p>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={rolAdmin} onChange={() => { setRolAdmin(!rolAdmin); cambiarRol('admin'); }} />
                  <span>Administrador</span>
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input type="checkbox" checked={rolFunc} onChange={() => { setRolFunc(!rolFunc); cambiarRol('funcionario'); }} />
                  <span>Funcionario</span>
                </label>
              </div>
              <div className="result">{resRoles}</div>
            </div>
          </div>
        )}
      </div>

      <div className="panel" style={{ gridColumn: '1 / -1' }}>
        <h2>Usuarios pendientes de validación</h2>
        <div className="actions" style={{ marginBottom: '12px' }}>
          <button className="btn outlined" onClick={cargarPendientes}><span className="material-symbols-outlined">refresh</span> Refrescar lista</button>
        </div>
        <div className="result">
          {pendientes === null ? (
            <span className="small-note">Cargando...</span>
          ) : pendientes.length === 0 ? (
            <span className="small-note">No hay usuarios pendientes de validación.</span>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>País doc</th>
                    <th>Tipo doc</th>
                    <th>Número doc</th>
                    <th>Fecha registro</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {pendientes.map(u => (
                    <tr key={u.email}>
                      <td>{u.email}</td>
                      <td>{u.docPais}</td>
                      <td>{u.docTipo}</td>
                      <td>{u.docNumero}</td>
                      <td>{u.fechaRegistro}</td>
                      <td>
                        <button className="btn" style={{ padding: '6px 16px', fontSize: '0.82rem' }} onClick={() => verificarUsuario(u.email, 'verificado')}>
                          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>check_circle</span> Verificar
                        </button>
                        <button className="btn danger" style={{ padding: '6px 16px', fontSize: '0.82rem', marginLeft: '4px' }} onClick={() => verificarUsuario(u.email, 'rechazado')}>
                          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>cancel</span> Rechazar
                        </button>
                      </td>
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
