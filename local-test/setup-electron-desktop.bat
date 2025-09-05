@echo off
echo ========================================
echo Setting up Electron Desktop Alternative
echo ========================================
echo.
echo This will create a proper desktop app using Electron
echo that judges can test end-to-end without build issues.
echo.

cd /d "%~dp0\.."

echo 📦 Installing Electron...
npm install --save-dev electron electron-builder concurrently wait-on

echo 📝 Creating Electron main process...
if not exist electron-main.js (
    echo Creating electron-main.js...
    echo const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron'^); > electron-main.js
    echo const path = require('path'^); >> electron-main.js
    echo const isDev = process.env.NODE_ENV === 'development'^; >> electron-main.js
    echo. >> electron-main.js
    echo let mainWindow^; >> electron-main.js
    echo. >> electron-main.js
    echo function createWindow(^) { >> electron-main.js
    echo   mainWindow = new BrowserWindow({ >> electron-main.js
    echo     width: 1200, >> electron-main.js
    echo     height: 800, >> electron-main.js
    echo     webPreferences: { >> electron-main.js
    echo       nodeIntegration: true, >> electron-main.js
    echo       contextIsolation: false >> electron-main.js
    echo     }, >> electron-main.js
    echo     icon: path.join(__dirname, 'public', 'icon.png'^), >> electron-main.js
    echo     titleBarStyle: 'default', >> electron-main.js
    echo     show: false >> electron-main.js
    echo   }^); >> electron-main.js
    echo. >> electron-main.js
    echo   const startUrl = isDev ? 'http://localhost:5173' : `file://${path.join(__dirname, '../dist/index.html'^)}`^; >> electron-main.js
    echo   mainWindow.loadURL(startUrl^); >> electron-main.js
    echo. >> electron-main.js
    echo   mainWindow.once('ready-to-show', (^) =^> { >> electron-main.js
    echo     mainWindow.show(^)^; >> electron-main.js
    echo   }^); >> electron-main.js
    echo. >> electron-main.js
    echo   // Register global shortcut for Aura overlay >> electron-main.js
    echo   globalShortcut.register('CommandOrControl+\'', (^) =^> { >> electron-main.js
    echo     if (mainWindow.isVisible(^)^) { >> electron-main.js
    echo       mainWindow.hide(^)^; >> electron-main.js
    echo     } else { >> electron-main.js
    echo       mainWindow.show(^)^; >> electron-main.js
    echo       mainWindow.focus(^)^; >> electron-main.js
    echo     } >> electron-main.js
    echo   }^); >> electron-main.js
    echo } >> electron-main.js
    echo. >> electron-main.js
    echo app.whenReady(^).then(createWindow^); >> electron-main.js
    echo. >> electron-main.js
    echo app.on('window-all-closed', (^) =^> { >> electron-main.js
    echo   if (process.platform !== 'darwin'^) app.quit(^)^; >> electron-main.js
    echo }^); >> electron-main.js
    echo. >> electron-main.js
    echo app.on('activate', (^) =^> { >> electron-main.js
    echo   if (BrowserWindow.getAllWindows(^).length === 0^) createWindow(^)^; >> electron-main.js
    echo }^); >> electron-main.js
)

echo 📝 Updating package.json for Electron...
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.main = 'electron-main.js';
pkg.scripts = pkg.scripts || {};
pkg.scripts['electron'] = 'electron .';
pkg.scripts['electron:dev'] = 'concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"';
pkg.scripts['electron:build'] = 'npm run build && electron-builder';
pkg.scripts['desktop:demo'] = 'npm run electron:dev';
pkg.build = {
  appId: 'com.aura.desktop-assistant',
  productName: 'Aura Desktop Assistant',
  directories: {
    output: 'dist-electron'
  },
  files: [
    'dist/**/*',
    'electron-main.js',
    'package.json'
  ],
  win: {
    target: 'nsis',
    icon: 'public/icon.ico'
  }
};
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
console.log('✅ Package.json updated for Electron');
"

echo ✅ Electron desktop setup complete!
echo.
echo 🚀 To run the desktop app:
echo    npm run desktop:demo
echo.
echo 📦 To build distributable:
echo    npm run electron:build
echo.
pause