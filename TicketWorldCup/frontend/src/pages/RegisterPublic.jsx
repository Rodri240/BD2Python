import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

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

export default function RegisterPublic() {
  const [form, setForm] = useState({
    email: '', passw: '', docPais: '', docTipo: '', docNumero: '',
    dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', telefonos: ''
  });
  const [result, setResult] = useState('');
  const [success, setSuccess] = useState(false);

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }));

  const handleRegister = async () => {
    const { email, passw, docPais, docTipo, docNumero, dirPais, dirLocalidad, dirCalle, dirNumero, dirCodigoPostal } = form;
    if (!email || !passw || !docPais || !docTipo || !docNumero || !dirPais || !dirLocalidad || !dirCalle || !dirNumero || !dirCodigoPostal) {
      setResult('<span style="color:var(--md-error);">Completá todos los campos obligatorios.</span>');
      return;
    }
    try {
      const res = await fetch('/registrarse', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok || data.ok === false) {
        setResult('<span style="color:var(--md-error);">' + (data.error || 'Error al registrarse') + '</span>');
        return;
      }
      setSuccess(true);
      setResult(`
        <div style="color:var(--md-primary);font-weight:500;margin-bottom:8px;">
          <span class="material-symbols-outlined" style="vertical-align:middle;font-size:18px;">check_circle</span>
          ¡Cuenta creada correctamente!
        </div>
        <p style="font-size:0.88rem;color:var(--md-on-surface-variant);">
          Ya podés <a href="/login" style="color:var(--md-primary);font-weight:500;">iniciar sesión</a> con tu email y contraseña.
        </p>
      `);
      setForm({ email: '', passw: '', docPais: '', docTipo: '', docNumero: '', dirPais: '', dirLocalidad: '', dirCalle: '', dirNumero: '', dirCodigoPostal: '', telefonos: '' });
    } catch (err) {
      setResult('<span style="color:var(--md-error);">' + err.message + '</span>');
    }
  };

  const selStyle = { appearance: 'auto' };

  return (
    <section className="page-grid" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.2fr)', alignItems: 'start', minHeight: 'calc(100vh - 180px)' }}>
      <div className="hero-card" style={{ position: 'sticky', top: '24px' }}>
        <p className="eyebrow">Nuevo usuario</p>
        <h1>Creá tu cuenta</h1>
        <p className="hero-copy">Registrate para comprar entradas al Mundial 2026, transferirlas y gestionar tus activos digitales.</p>
        <div className="badge-row">
          <span className="badge"><span className="material-symbols-outlined">confirmation_number</span> Compra de entradas</span>
          <span className="badge"><span className="material-symbols-outlined">swap_horiz</span> Transferencias</span>
          <span className="badge"><span className="material-symbols-outlined">qr_code</span> QR dinámico</span>
        </div>
        <p style={{ marginTop: '24px', fontSize: '0.88rem', color: 'var(--md-on-surface-variant)' }}>
          ¿Ya tenés cuenta? <Link to="/login" style={{ color: 'var(--md-primary)', textDecoration: 'none', fontWeight: 500 }}>Iniciá sesión</Link>
        </p>
      </div>
      <div className="panel">
        <h2>Datos personales</h2>
        <div className="form-grid">
          <input type="email" placeholder="Email *" className="full" value={form.email} onChange={set('email')} />
          <input type="password" placeholder="Contraseña *" className="full" value={form.passw} onChange={set('passw')} />
          <select style={selStyle} value={form.docPais} onChange={set('docPais')}>
            <option value="">País del documento *</option>
            {PAISES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <select style={selStyle} value={form.docTipo} onChange={set('docTipo')}>
            <option value="">Tipo de documento *</option>
            <option value="CI">Cédula de Identidad (CI)</option>
            <option value="DNI">Documento Nacional de Identidad (DNI)</option>
            <option value="PAS">Pasaporte</option>
            <option value="SSN">Número de Seguro Social (SSN - USA)</option>
          </select>
          <input placeholder="Número de documento *" className="full" value={form.docNumero} onChange={set('docNumero')} />
          <select style={selStyle} value={form.dirPais} onChange={set('dirPais')}>
            <option value="">País (dirección) *</option>
            {PAISES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <input placeholder="Localidad *" value={form.dirLocalidad} onChange={set('dirLocalidad')} />
          <input placeholder="Calle *" value={form.dirCalle} onChange={set('dirCalle')} />
          <input placeholder="Número *" value={form.dirNumero} onChange={set('dirNumero')} />
          <input placeholder="Código postal *" value={form.dirCodigoPostal} onChange={set('dirCodigoPostal')} />
          <input placeholder="Teléfonos de Contacto (separados por coma)" className="full" value={form.telefonos} onChange={set('telefonos')} />
        </div>
        <div className="actions" style={{ marginTop: '20px' }}>
          <button className="btn" onClick={handleRegister} disabled={success}>
            <span className="material-symbols-outlined">person_add</span> Crear cuenta
          </button>
          <Link className="btn outlined" to="/login">
            <span className="material-symbols-outlined">arrow_back</span> Volver
          </Link>
        </div>
        <div className="result" dangerouslySetInnerHTML={{ __html: result }} />
      </div>
    </section>
  );
}
