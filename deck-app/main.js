const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const fs = require('fs');

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

function createWindow() {
    const pcIp = getPcIp();

    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        backgroundColor: '#0a0d14',
        fullscreen: process.platform === 'linux',
        kiosk: process.platform === 'linux',
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

    // Strip frame restrictions on the webview partition session
    const partitionSession = session.fromPartition('persist:companion');
    partitionSession.webRequest.onHeadersReceived((details, callback) => {
        const responseHeaders = { ...details.responseHeaders };
        delete responseHeaders['x-frame-options'];
        delete responseHeaders['X-Frame-Options'];
        delete responseHeaders['content-security-policy'];
        delete responseHeaders['Content-Security-Policy'];
        callback({ cancel: false, responseHeaders });
    });

    mainWindow.loadFile(path.join(__dirname, 'index.html'), {
        query: { pc_ip: pcIp }
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
