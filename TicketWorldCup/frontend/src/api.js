const BASE = '';

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderJson(value) {
  if (value === null || value === undefined) {
    return '<span class="small-note">Sin Datos</span>';
  }
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return escapeHtml(value);
  }
  if (Array.isArray(value)) {
    if (!value.length) {
      return '<span class="small-note">Sin Datos</span>';
    }
    const headers = [...new Set(value.flatMap((item) => (item && typeof item === 'object' && !Array.isArray(item)) ? Object.keys(item) : []))];
    if (!headers.length) {
      return `<ul>${value.map((item) => `<li>${renderJson(item)}</li>`).join('')}</ul>`;
    }
    const head = headers.map((header) => `<th>${escapeHtml(header)}</th>`).join('');
    const body = value.map((row) => {
      const cells = headers.map((header) => `<td>${renderJson(row?.[header])}</td>`).join('');
      return `<tr>${cells}</tr>`;
    }).join('');
    return `<div style="overflow-x:auto;"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
  }
  if (typeof value === 'object') {
    const entries = Object.entries(value);
    if (!entries.length) {
      return '<span class="small-note">Sin Datos</span>';
    }
    const rows = entries.map(([key, item]) => `
      <tr>
        <th>${escapeHtml(key)}</th>
        <td>${renderJson(item)}</td>
      </tr>
    `).join('');
    return `<div style="overflow-x:auto;"><table><tbody>${rows}</tbody></table></div>`;
  }
  return escapeHtml(String(value));
}

async function requestJSON(url, options = {}) {
  const response = await fetch(BASE + url, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

async function post(url, body) {
  return requestJSON(url, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export {
  renderJson,
  requestJSON,
  post,
};
