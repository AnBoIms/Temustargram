import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // 포트를 3000번으로 변경
    host: '0.0.0.0',
    strictPort: true,
  },
});
