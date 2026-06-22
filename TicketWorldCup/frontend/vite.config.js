import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/static/',
  build: {
    outDir: '../static',
    emptyOutDir: true,
  },
  server: {
    proxy: [{
      context: [
        '/api', '/sesion', '/salir', '/login', '/logout', '/registrarse',
        '/registrar', '/dispositivo', '/dispositivos',
        '/estadio', '/estadios', '/sector', '/sectores',
        '/evento', '/eventos', '/vinculaciones', '/equipos',
        '/usuarios', '/usuario', '/comprar', '/compras',
        '/ventas', '/venta', '/transferencia', '/transferencias',
        '/entrada', '/mi-entrada', '/validar',
        '/funcionario', '/funcionarios', '/asignacion',
        '/ranking',
      ],
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
    }],
  },
})
