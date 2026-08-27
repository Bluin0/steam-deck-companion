// Auto-relaunch on Linux/SteamOS if required CLI flags are missing.
// This ensures that double-clicking the .AppImage or launching from Steam/Dolphin
// without terminal arguments will ALWAYS start with --no-sandbox and --disable-dev-shm-usage.
if (process.platform === 'linux') {
    const requiredFlags = ['--no-sandbox', '--disable-dev-shm-usage'];
    const missingFlags = requiredFlags.filter(f => !process.argv.includes(f));

    if (missingFlags.length > 0 && !process.env.SDC_RELAUNCHED) {
        const { spawn } = require('child_process');
        const targetBin = process.env.APPIMAGE || process.execPath;
        const child = spawn(targetBin, [...missingFlags, ...process.argv.slice(1)], {
            detached: true,
            stdio: 'inherit',
            env: { ...process.env, SDC_RELAUNCHED: '1' }
        });
        child.unref();
        process.exit(0);
    }
}

const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const fs = require('fs');

// ── SteamOS / Linux Compatibility ──
if (process.platform === 'linux') {
    app.commandLine.appendSwitch('no-sandbox');
    app.commandLine.appendSwitch('disable-dev-shm-usage');
    app.commandLine.appendSwitch('disable-gpu-sandbox');
    app.commandLine.appendSwitch('disable-setuid-sandbox');
    app.commandLine.appendSwitch('touch-events', 'enabled');
    app.commandLine.appendSwitch('enable-touch-drag-drop');
    app.commandLine.appendSwitch('enable-pinch');
    app.commandLine.appendSwitch('log-level', '3');
}

let mainWindow = null;

function getPcIp() {
    // 1. Check command-line argument: --pc-ip=192.168.1.100
    for (const arg of process.argv) {
        if (arg.startsWith('--pc-ip=')) {
            return arg.split('=')[1].trim();
        }
    }

    // 2. Check config file in user data
    const ipFile = path.join(app.getPath('userData'), 'pc_ip.txt');
    if (fs.existsSync(ipFile)) {
        try {
            return fs.readFileSync(ipFile, 'utf-8').trim();
        } catch (e) {
            console.error('Error reading pc_ip.txt:', e);
        }
    }

    // 3. Check ~/.local/share/steam-deck-companion/pc_ip.txt
    const deckIpFile = path.join(process.env.HOME || '', '.local/share/steam-deck-companion/pc_ip.txt');
    if (fs.existsSync(deckIpFile)) {
        try {
            return fs.readFileSync(deckIpFile, 'utf-8').trim();
        } catch (e) {}
    }

    return '127.0.0.1';
}

// Synchronous IPC handler for renderer to get initial PC IP
ipcMain.on('get-pc-ip', (event) => {
    event.returnValue = getPcIp();
});

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        backgroundColor: '#0a0d14',
        fullscreen: process.platform === 'linux',
        autoHideMenuBar: true,
        frame: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webviewTag: true,
            allowRunningInsecureContent: true,
            webSecurity: false,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    // Strip frame restrictions and block heavy ad/tracking domains on the webview partition session
    const partitionSession = session.fromPartition('persist:companion');

    const blockedTrackerPatterns = [
        '*://*.doubleclick.net/*',
        '*://*.googlesyndication.com/*',
        '*://*.google-analytics.com/*',
        '*://*.kueez.com/*',
        '*://*.adnxs.com/*',
        '*://*.outbrain.com/*',
        '*://*.taboola.com/*',
        '*://*.criteo.com/*',
        '*://*.scorecardresearch.com/*',
        '*://*.amazon-adsystem.com/*',
        '*://*.pubmatic.com/*',
        '*://*.rubiconproject.com/*',
        '*://*.casalemedia.com/*',
        '*://*.openx.net/*'
    ];

    partitionSession.webRequest.onBeforeRequest({ urls: blockedTrackerPatterns }, (details, callback) => {
        callback({ cancel: true });
    });

    partitionSession.webRequest.onHeadersReceived((details, callback) => {
        const responseHeaders = { ...details.responseHeaders };
        delete responseHeaders['x-frame-options'];
        delete responseHeaders['X-Frame-Options'];
        delete responseHeaders['content-security-policy'];
        delete responseHeaders['Content-Security-Policy'];
        callback({ cancel: false, responseHeaders });
    });

    // Load clean index.html path without query parameters to prevent ASAR lookup failure
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
        console.error('[WebContents] Load failed:', errorCode, errorDescription, validatedURL);
    });

    mainWindow.webContents.on('render-process-gone', (event, details) => {
        console.error('[WebContents] Render process crashed! Reason:', details.reason, 'exitCode:', details.exitCode);
    });

    // F12 or Ctrl+Shift+I toggles DevTools for easy debugging
    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.key === 'F12' || (input.control && input.shift && input.key.toLowerCase() === 'i')) {
            mainWindow.webContents.toggleDevTools();
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

// Silence benign navigation aborts
process.on('unhandledRejection', (reason) => {
    const strReason = String(reason || '');
    if (reason && (reason.errno === -3 || reason.code === 'ERR_ABORTED' || strReason.includes('ERR_ABORTED') || strReason.includes('-3'))) {
        return;
    }
    console.warn('[Process] Unhandled Rejection:', reason);
});
