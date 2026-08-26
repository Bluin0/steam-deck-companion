const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('deckApp', {
    isNative: true,
    platform: process.platform
});
