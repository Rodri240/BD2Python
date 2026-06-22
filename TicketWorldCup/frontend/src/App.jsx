import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ErrorPage from './components/ErrorPage';
import SessionGuard from './components/SessionGuard';
import Principal from './pages/Principal';
import Login from './pages/Login';
import RegisterPublic from './pages/RegisterPublic';
import Home from './pages/Home';
import Perfil from './pages/Perfil';
import Registro from './pages/Registro';
import Infraestructura from './pages/Infraestructura';
import Compras from './pages/Compras';
import Transferencias from './pages/Transferencias';
import Validacion from './pages/Validacion';
import Consultas from './pages/Consultas';

const router = createBrowserRouter([
  {
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
      { path: '/principal', element: <Principal /> },
      { path: '/login', element: <Login /> },
      { path: '/registrarse', element: <RegisterPublic /> },
      {
        element: <SessionGuard />,
        errorElement: <ErrorPage />,
        children: [
          { index: true, element: <Home /> },
          { path: 'perfil', element: <Perfil /> },
          { path: 'registro', element: <Registro /> },
          { path: 'infraestructura', element: <Infraestructura /> },
          { path: 'compras', element: <Compras /> },
          { path: 'transferencias', element: <Transferencias /> },
          { path: 'validacion', element: <Validacion /> },
          { path: 'consultas', element: <Consultas /> },
        ],
      },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);

export default router;
