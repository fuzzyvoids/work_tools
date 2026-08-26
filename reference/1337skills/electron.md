# Electron Cheat Sheet intermediate

## Overview

Electron is an open-source framework maintained by GitHub/Microsoft that enables developers to build cross-platform desktop applications using web technologies. It combines the Chromium rendering engine with the Node.js runtime, allowing full access to both web APIs and native system capabilities from a single JavaScript codebase. Applications built with Electron run on Windows, macOS, and Linux, and notable production apps include Visual Studio Code, Slack, Discord, Figma, and Notion.

Electron uses a multi-process architecture with a main process (Node.js) that manages application lifecycle, native OS interactions, and window creation, and renderer processes (Chromium) that display the web UI. Inter-process communication (IPC) bridges these two worlds. While Electron apps are larger than native apps due to bundling Chromium, the framework offers unmatched developer productivity for teams with web expertise, extensive ecosystem support, and a mature plugin system through native Node.js modules.

## Installation

```bash
# Initialize a new project
mkdir my-electron-app && cd my-electron-app
npm init -y

# Install Electron
npm install --save-dev electron

# Or use a boilerplate
npx create-electron-app@latest my-app
cd my-app

# Using Electron Forge (recommended)
npm init electron-app@latest my-app -- --template=webpack-typescript
cd my-app

# Using Electron Vite (modern alternative)
npm create @quick-start/electron my-app
cd my-app

# Verify installation
npx electron --version
```

## Project Structure

```plaintext
my-electron-app/
|-- package.json
|-- main.js              # Main process entry
|-- preload.js           # Preload script (bridge)
|-- renderer/
|   |-- index.html       # UI entry point
|   |-- renderer.js      # Renderer process code
|   `-- styles.css
|-- src/                 # Application source
|   |-- main/
|   |   |-- index.ts     # Main process
|   |   `-- ipc.ts       # IPC handlers
|   `-- renderer/
|       |-- App.tsx       # React/Vue/Svelte app
|       `-- index.html
|-- resources/           # App icons and assets
|-- forge.config.js      # Electron Forge config
`-- electron-builder.yml # electron-builder config
```

## Main Process

```javascript
// main.js
const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 600,
        minHeight: 400,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,    // Security: always true
            nodeIntegration: false,     // Security: always false
            sandbox: true
        },
        titleBarStyle: 'hiddenInset', // macOS frameless
        icon: path.join(__dirname, 'resources/icon.png')
    });

    // Load app
    if (process.env.NODE_ENV === 'development') {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile('dist/index.html');
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
```

## Preload Script

```javascript
// preload.js - Bridge between main and renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // File operations
    openFile: () => ipcRenderer.invoke('dialog:openFile'),
    saveFile: (content) => ipcRenderer.invoke('dialog:saveFile', content),
    readFile: (path) => ipcRenderer.invoke('fs:readFile', path),

    // App info
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPlatform: () => process.platform,

    // Events from main process
    onUpdateAvailable: (callback) =>
        ipcRenderer.on('update-available', (_event, info) => callback(info)),
    onProgress: (callback) =>
        ipcRenderer.on('progress', (_event, value) => callback(value)),

    // Send to main
    sendMessage: (channel, data) => {
        const validChannels = ['toMain', 'minimize', 'maximize', 'close'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    }
});
```

## IPC Communication

```javascript
// Main process - handle IPC
const { ipcMain, dialog } = require('electron');
const fs = require('fs/promises');

// Handle invoke (async request/response)
ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        filters: [
            { name: 'Text Files', extensions: ['txt', 'md'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    });
    if (result.canceled) return null;
    const content = await fs.readFile(result.filePaths[0], 'utf-8');
    return { path: result.filePaths[0], content };
});

ipcMain.handle('dialog:saveFile', async (event, content) => {
    const result = await dialog.showSaveDialog({
        filters: [{ name: 'Text', extensions: ['txt'] }]
    });
    if (!result.canceled) {
        await fs.writeFile(result.filePath, content, 'utf-8');
        return result.filePath;
    }
    return null;
});

ipcMain.handle('app:getVersion', () => app.getVersion());

// Handle one-way messages
ipcMain.on('minimize', () => mainWindow.minimize());
ipcMain.on('maximize', () => {
    mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
});
ipcMain.on('close', () => mainWindow.close());
```

```javascript
// Renderer process - use exposed APIs
document.getElementById('openBtn').addEventListener('click', async () => {
    const file = await window.electronAPI.openFile();
    if (file) {
        document.getElementById('editor').value = file.content;
    }
});

window.electronAPI.onProgress((value) => {
    document.getElementById('progress').style.width = `${value}%`;
});
```

## Menus

```javascript
const { Menu, MenuItem } = require('electron');

const template = [
    {
        label: 'File',
        submenu: [
            { label: 'New', accelerator: 'CmdOrCtrl+N', click: () => createNewFile() },
            { label: 'Open', accelerator: 'CmdOrCtrl+O', click: () => openFile() },
            { label: 'Save', accelerator: 'CmdOrCtrl+S', click: () => saveFile() },
            { type: 'separator' },
            { role: 'quit' }
        ]
    },
    {
        label: 'Edit',
        submenu: [
            { role: 'undo' },
            { role: 'redo' },
            { type: 'separator' },
            { role: 'cut' },
            { role: 'copy' },
            { role: 'paste' },
            { role: 'selectAll' }
        ]
    },
    {
        label: 'View',
        submenu: [
            { role: 'reload' },
            { role: 'forceReload' },
            { role: 'toggleDevTools' },
            { type: 'separator' },
            { role: 'zoomIn' },
            { role: 'zoomOut' },
            { role: 'resetZoom' },
            { type: 'separator' },
            { role: 'togglefullscreen' }
        ]
    }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
```

## Configuration

```json
// package.json
{
  "name": "my-electron-app",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "electron . --enable-logging",
    "build": "electron-builder",
    "build:mac": "electron-builder --mac",
    "build:win": "electron-builder --win",
    "build:linux": "electron-builder --linux",
    "pack": "electron-builder --dir"
  }
}
```

```yaml
# electron-builder.yml
appId: com.example.myapp
productName: My App
directories:
  output: release
  buildResources: resources
files:
  - "**/*"
  - "!src/**"
mac:
  target:
    - dmg
    - zip
  category: public.app-category.developer-tools
  hardenedRuntime: true
win:
  target:
    - nsis
    - portable
linux:
  target:
    - AppImage
    - deb
    - snap
  category: Utility
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
publish:
  provider: github
```

## Build and Distribute

```bash
# Build with electron-builder
npx electron-builder --mac --win --linux

# Build specific platform
npx electron-builder --mac dmg
npx electron-builder --win nsis
npx electron-builder --linux AppImage

# With Electron Forge
npx electron-forge make
npx electron-forge publish

# Code signing (macOS)
export CSC_LINK="path/to/certificate.p12"
export CSC_KEY_PASSWORD="password"
npx electron-builder --mac

# Auto-update setup
npm install electron-updater
```

## Advanced Usage

```javascript
// System tray
const { Tray, nativeImage } = require('electron');

let tray;
app.whenReady().then(() => {
    const icon = nativeImage.createFromPath('resources/tray-icon.png');
    tray = new Tray(icon.resize({ width: 16, height: 16 }));

    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show App', click: () => mainWindow.show() },
        { label: 'Quit', click: () => app.quit() }
    ]);

    tray.setToolTip('My Electron App');
    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => mainWindow.show());
});

// Notifications
const { Notification } = require('electron');
new Notification({
    title: 'Update Available',
    body: 'A new version is ready to install.',
    icon: 'resources/icon.png'
}).show();

// Global shortcuts
const { globalShortcut } = require('electron');
app.whenReady().then(() => {
    globalShortcut.register('CommandOrControl+Shift+I', () => {
        mainWindow.webContents.toggleDevTools();
    });
});

// Native file drag
mainWindow.webContents.on('will-navigate', (event) => {
    event.preventDefault(); // Prevent navigation on file drop
});
```

## Troubleshooting

| Issue | Solution |
| --- | --- |
| White screen on load | Check `loadFile`/`loadURL` path; check console for errors |
| `require` not defined in renderer | Use preload script with `contextBridge`; never enable `nodeIntegration` |
| App too large | Use `electron-builder` asar packing; exclude unnecessary files |
| High memory usage | Profile with DevTools; close unused windows; watch for memory leaks |
| macOS notarization fails | Use `electron-notarize` package; ensure hardened runtime enabled |
| Auto-update not working | Check `publish` config in builder; verify update server/GitHub releases |
| Native module build fails | Use `electron-rebuild`: `npx electron-rebuild` |
| CSP errors | Update Content-Security-Policy in HTML meta tag or webPreferences |
| Slow startup | Lazy-load modules; defer non-critical initialization |
| IPC not working | Ensure channel names match; check preload script is loaded correctly |

Source: https://1337skills.com/cheatsheets/electron/
