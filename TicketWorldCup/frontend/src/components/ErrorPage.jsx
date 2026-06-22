import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router-dom';

export default function ErrorPage() {
  const error = useRouteError();
  const navigate = useNavigate();

  let title = 'Algo salió mal';
  let message = 'Ocurrió un error inesperado.';

  if (isRouteErrorResponse(error)) {
    title = `${error.status} ${error.statusText}`;
    message = error.data?.message || message;
  } else if (error instanceof Error) {
    message = error.message;
  }

  return (
    <div className="error-page">
      <div className="error-page-card">
        <span className="material-symbols-outlined error-page-icon">error_outline</span>
        <h1>{title}</h1>
        <p>{message}</p>
        <div className="actions" style={{ justifyContent: 'center' }}>
          <button className="btn" onClick={() => navigate(-1)}>
            <span className="material-symbols-outlined">arrow_back</span> Volver
          </button>
          <button className="btn tonal" onClick={() => window.location.reload()}>
            <span className="material-symbols-outlined">refresh</span> Recargar
          </button>
        </div>
      </div>
    </div>
  );
}
