const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('deckApp', {
    isNative: true,
    platform: process.platform,
    getPcIp: () => {
        try {
            return ipcRenderer.sendSync('get-pc-ip');
        } catch (e) {
            return '127.0.0.1';
        }
    }
});
