import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(async () => ({
  plugins: [react()],

  // Vite options optimized for Electron development
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: false,
    host: 'localhost',
    watch: {
      // Ignore Tauri directory (legacy)
      ignored: ["**/src-tauri/**"],
    },
  },
  
  // Environment variables
  envPrefix: ['VITE_', 'ELECTRON_'],
  
  // Build configuration optimized for Electron
  build: {
    target: 'chrome120', // Modern Electron uses recent Chrome
    minify: 'esbuild',
    sourcemap: true,
    
    // Rollup options
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          xstate: ['xstate', '@xstate/react'],
        },
      },
    },
  },
  
  // CSS configuration
  css: {
    postcss: './postcss.config.js',
  },
  
  // Resolve configuration
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  
  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
}));