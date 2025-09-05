const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'public', 'aura-icon.svg'),
    titleBarStyle: 'default',
    show: false
  });

  const startUrl = isDev ? 'http://localhost:5173' : `file://${path.join(__dirname, 'dist/index.html')}`;
  console.log('🔗 Loading URL:', startUrl);
  console.log('📊 isDev:', isDev);
  console.log('🌍 NODE_ENV:', process.env.NODE_ENV);
  
  mainWindow.loadURL(startUrl);
  
  // Add error handling for load failures
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('❌ Failed to load:', validatedURL, errorCode, errorDescription);
  });
  
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('✅ Page loaded successfully');
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    console.log('🎉 Aura Desktop Assistant is ready!');
    console.log('Press Ctrl+\' to activate voice mode');
  });

  // Register global shortcut for Aura overlay
  globalShortcut.register('CommandOrControl+\'', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  createWindow();
  console.log('🚀 Aura Desktop Assistant started successfully!');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    globalShortcut.unregisterAll();
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});