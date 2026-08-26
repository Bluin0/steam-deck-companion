/**
 * Steam Deck Companion — Native App Client (Electron WebView)
 */

// Determine PC IP
const urlParams = new URLSearchParams(window.location.search);
const PC_IP = urlParams.get('pc_ip') || window.location.hostname || '127.0.0.1';
const WS_PORT = 8765;
const HTTP_PORT = 8080;
const wsUrl = `ws://${PC_IP}:${WS_PORT}`;

// State
let ws = null;
let currentGame = null;
let currentProfile = null;
let installedGames = [];
let sessionStartTime = Date.now();
let timerInterval = null;
let notesSaveTimeout = null;
let activeTabId = 'overview';
let currentWebHomeUrl = 'https://www.google.com';
let currentZoomFactor = 1.0;

// DOM Elements
const connBadge = document.getElementById('connBadge');
const connText = document.getElementById('connText');
const gameTitle = document.getElementById('gameTitle');
const gameCover = document.getElementById('gameCover');
const gameCoverPlaceholder = document.getElementById('gameCoverPlaceholder');
const sessionTimer = document.getElementById('sessionTimer');
const sidebarTabs = document.getElementById('sidebarTabs');

// Views
const viewOverview = document.getElementById('view-overview');
const viewWeb = document.getElementById('view-web');
const viewNotes = document.getElementById('view-notes');
const webFrame = document.getElementById('webFrame');
const webviewLoader = document.getElementById('webviewLoader');
const webTabTitle = document.getElementById('webTabTitle');

// Webview Controls
const btnWebBack = document.getElementById('btnWebBack');
const btnWebForward = document.getElementById('btnWebForward');
const btnWebReload = document.getElementById('btnWebReload');
const btnWebHome = document.getElementById('btnWebHome');
const btnWebZoomIn = document.getElementById('btnWebZoomIn');
const btnWebZoomOut = document.getElementById('btnWebZoomOut');

// Overview Elements
const overviewTitle = document.getElementById('overviewTitle');
const overviewSubtitle = document.getElementById('overviewSubtitle');
const overviewAppId = document.getElementById('overviewAppId');
const overviewPid = document.getElementById('overviewPid');
const cardQuickHltb = document.getElementById('cardQuickHltb');
const cardQuickNotes = document.getElementById('cardQuickNotes');

// Notes Elements
const notesArea = document.getElementById('notesArea');
const notesStatus = document.getElementById('notesStatus');
const btnClearNotes = document.getElementById('btnClearNotes');

// Modal Elements
const gameModal = document.getElementById('gameModal');
const btnOpenPicker = document.getElementById('btnOpenPicker');
const btnCloseModal = document.getElementById('btnCloseModal');
const gameSearchInput = document.getElementById('gameSearchInput');
const gamesList = document.getElementById('gamesList');

// ================= WebSocket & State =================

function connectWebSocket() {
    connText.textContent = 'PC...';
    connBadge.classList.remove('connected');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        connText.textContent = 'PC';
        connBadge.classList.add('connected');
        console.log('[WS] Connected to PC Companion server:', wsUrl);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'init') {
                installedGames = data.installed_games || [];
                handleGameUpdate(data.game, data.profile, data.notes);
            } else if (data.type === 'game_update') {
                handleGameUpdate(data.game, data.profile, data.notes);
            } else if (data.type === 'notes_saved') {
                notesStatus.textContent = 'Guardado en PC ✓';
                setTimeout(() => { notesStatus.textContent = 'Guardado en PC'; }, 2000);
            }
        } catch (e) {
            console.error('[WS] Error processing message:', e);
        }
    };

    ws.onclose = () => {
        connText.textContent = 'Desconectado';
        connBadge.classList.remove('connected');
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error('[WS] Socket error:', err);
    };
}

function handleGameUpdate(game, profile, notes) {
    const isNewGame = !currentGame || (game && currentGame.appid !== game.appid);
    currentGame = game;
    currentProfile = profile;

    if (isNewGame) {
        sessionStartTime = Date.now();
    }

    updateHeaderUI();
    renderTabs();
    if (notes !== undefined) {
        notesArea.value = notes || '';
    }

    // Default to Overview if active tab is not in profile
    if (!profile.tabs.find(t => t.id === activeTabId)) {
        switchTab('overview');
    }
}

// ================= UI Updates =================

function updateHeaderUI() {
    if (currentGame && currentGame.name) {
        gameTitle.textContent = currentGame.name;
        overviewTitle.textContent = currentGame.name;
        overviewSubtitle.textContent = `En ejecución en PC (PID: ${currentGame.pid || '--'})`;
        overviewAppId.textContent = `AppID: ${currentGame.appid || '--'}`;
        overviewPid.textContent = `PID: ${currentGame.pid || '--'}`;

        if (currentGame.appid && currentGame.appid !== 'default' && !currentGame.appid.startsWith('custom_')) {
            const coverUrl = `https://cdn.cloudflare.steamstatic.com/steam/apps/${currentGame.appid}/header.jpg`;
            gameCover.src = coverUrl;
            gameCover.onload = () => {
                gameCover.classList.remove('hidden');
                gameCoverPlaceholder.style.display = 'none';
            };
            gameCover.onerror = () => {
                gameCover.classList.add('hidden');
                gameCoverPlaceholder.style.display = 'flex';
            };
        } else {
            gameCover.classList.add('hidden');
            gameCoverPlaceholder.style.display = 'flex';
        }
    } else {
        gameTitle.textContent = 'Sin juego detectado';
        overviewTitle.textContent = 'Sin juego detectado';
        overviewSubtitle.textContent = 'Inicia un juego en el PC o selecciónalo manualmente desde el botón "Juegos".';
        overviewAppId.textContent = 'AppID: --';
        overviewPid.textContent = 'PID: --';
        gameCover.classList.add('hidden');
        gameCoverPlaceholder.style.display = 'flex';
    }
}

function startSessionTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        const hours = String(Math.floor(elapsed / 3600)).padStart(2, '0');
        const minutes = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
        const seconds = String(elapsed % 60).padStart(2, '0');
        sessionTimer.textContent = `⏱️ ${hours}:${minutes}:${seconds}`;
    }, 1000);
}

function renderTabs() {
    sidebarTabs.innerHTML = '';
    if (!currentProfile || !currentProfile.tabs) return;

    currentProfile.tabs.forEach((tab) => {
        const btn = document.createElement('button');
        btn.className = `tab-btn ${tab.id === activeTabId ? 'active' : ''}`;
        btn.innerHTML = `<span class="tab-icon">${tab.icon || '📌'}</span><span>${tab.name}</span>`;
        btn.onclick = () => switchTab(tab.id);
        sidebarTabs.appendChild(btn);
    });
}

function switchTab(tabId) {
    activeTabId = tabId;
    renderTabs();

    const tab = currentProfile ? currentProfile.tabs.find(t => t.id === tabId) : null;
    if (!tab) return;

    // Hide all views
    viewOverview.classList.remove('active');
    viewWeb.classList.remove('active');
    viewNotes.classList.remove('active');

    if (tab.type === 'overview') {
        viewOverview.classList.add('active');
    } else if (tab.type === 'notes') {
        viewNotes.classList.add('active');
    } else if (tab.type === 'web') {
        viewWeb.classList.add('active');
        if (webTabTitle) webTabTitle.textContent = tab.name || 'Visor Web';

        const gName = (currentGame && currentGame.name && currentGame.name !== 'Sin juego detectado') ? currentGame.name : '';
        const resolvedUrl = (tab.url || '').replace(/\{game_name\}/g, encodeURIComponent(gName));
        currentWebHomeUrl = resolvedUrl;

        if (webFrame.getAttribute('src') !== resolvedUrl) {
            webviewLoader.classList.add('active');
            webFrame.setAttribute('src', resolvedUrl);
        }
    }
}

// ================= Native WebView Setup =================

function setupWebview() {
    if (!webFrame) return;

    webFrame.addEventListener('did-start-loading', () => {
        webviewLoader.classList.add('active');
    });

    webFrame.addEventListener('did-stop-loading', () => {
        webviewLoader.classList.remove('active');
    });

    webFrame.addEventListener('did-fail-load', (e) => {
        if (e.errorCode !== -3) { // Ignore aborted loads
            webviewLoader.classList.remove('active');
            console.warn('[WebView] Load failed:', e);
        }
    });

    // Keep popups and clicked links inside the same webview
    webFrame.addEventListener('new-window', (e) => {
        e.preventDefault();
        webFrame.loadURL(e.url);
    });
}

// Webview Navigation Buttons
if (btnWebBack) {
    btnWebBack.addEventListener('click', () => {
        if (webFrame && webFrame.canGoBack()) webFrame.goBack();
    });
}

if (btnWebForward) {
    btnWebForward.addEventListener('click', () => {
        if (webFrame && webFrame.canGoForward()) webFrame.goForward();
    });
}

if (btnWebReload) {
    btnWebReload.addEventListener('click', () => {
        if (webFrame) webFrame.reload();
    });
}

if (btnWebHome) {
    btnWebHome.addEventListener('click', () => {
        if (webFrame && currentWebHomeUrl) {
            webFrame.loadURL(currentWebHomeUrl);
        }
    });
}

if (btnWebZoomIn) {
    btnWebZoomIn.addEventListener('click', () => {
        if (webFrame) {
            currentZoomFactor = Math.min(2.0, currentZoomFactor + 0.1);
            webFrame.setZoomFactor(currentZoomFactor);
        }
    });
}

if (btnWebZoomOut) {
    btnWebZoomOut.addEventListener('click', () => {
        if (webFrame) {
            currentZoomFactor = Math.max(0.6, currentZoomFactor - 0.1);
            webFrame.setZoomFactor(currentZoomFactor);
        }
    });
}

// ================= Notes Handling =================

notesArea.addEventListener('input', () => {
    notesStatus.textContent = 'Guardando...';
    if (notesSaveTimeout) clearTimeout(notesSaveTimeout);

    notesSaveTimeout = setTimeout(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const appid = currentGame ? currentGame.appid : 'default';
            ws.send(JSON.stringify({
                type: 'save_notes',
                appid: appid,
                content: notesArea.value
            }));
        }
    }, 800);
});

btnClearNotes.addEventListener('click', () => {
    if (confirm('¿Vaciar las notas de este juego?')) {
        notesArea.value = '';
        notesArea.dispatchEvent(new Event('input'));
    }
});

// Overview Quick Cards
if (cardQuickHltb) cardQuickHltb.addEventListener('click', () => switchTab('hltb'));
if (cardQuickNotes) cardQuickNotes.addEventListener('click', () => switchTab('notes'));

// ================= Game Selector Modal =================

btnOpenPicker.addEventListener('click', () => {
    renderModalGames(installedGames, '');
    gameModal.classList.remove('hidden');
    gameSearchInput.value = '';
    gameSearchInput.focus();
});

btnCloseModal.addEventListener('click', () => {
    gameModal.classList.add('hidden');
});

let gameSearchDebounce = null;

gameSearchInput.addEventListener('input', (e) => {
    const rawQuery = e.target.value.trim();
    if (gameSearchDebounce) clearTimeout(gameSearchDebounce);

    gameSearchDebounce = setTimeout(async () => {
        if (!rawQuery) {
            renderModalGames(installedGames, '');
            return;
        }

        const query = rawQuery.toLowerCase();
        // 1. Filter local installed games
        const localMatches = installedGames.filter(g => g.name.toLowerCase().includes(query)).map(g => ({
            ...g,
            source: 'installed'
        }));

        // 2. Query global Steam games through PC server
        let onlineMatches = [];
        try {
            const resp = await fetch(`http://${PC_IP}:${HTTP_PORT}/api/search_games?q=${encodeURIComponent(rawQuery)}`);
            if (resp.ok) {
                const data = await resp.json();
                const seen = new Set(localMatches.map(m => m.appid));
                onlineMatches = data.filter(item => !seen.has(item.appid)).map(item => ({
                    ...item,
                    source: 'steam'
                }));
            }
        } catch (err) {
            console.warn('[Search] Online game search error:', err);
        }

        const combined = [...localMatches, ...onlineMatches];
        renderModalGames(combined, rawQuery);
    }, 250);
});

function renderModalGames(list, currentQuery) {
    gamesList.innerHTML = '';

    if (currentQuery) {
        const customItem = document.createElement('div');
        customItem.className = 'game-item game-item-custom';
        customItem.innerHTML = `
            <span class="game-item-icon">✨</span>
            <div class="game-item-info">
                <span class="game-item-name">Usar "${currentQuery}" (Juego personalizado)</span>
                <span class="game-badge badge-custom">Personalizado</span>
            </div>
        `;
        customItem.onclick = () => {
            selectGame('custom_' + Date.now(), currentQuery);
        };
        gamesList.appendChild(customItem);
    }

    if (!list.length && !currentQuery) {
        gamesList.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-secondary);">Escribe el nombre de cualquier juego...</div>';
        return;
    }

    list.forEach(game => {
        const item = document.createElement('div');
        item.className = 'game-item';
        const badgeHtml = game.source === 'installed' 
            ? '<span class="game-badge badge-installed">Instalado</span>' 
            : '<span class="game-badge badge-steam">Steam</span>';
        
        const imgHtml = game.img 
            ? `<img src="${game.img}" class="game-item-thumb" alt="${game.name}">` 
            : '<span class="game-item-icon">🎮</span>';

        item.innerHTML = `
            ${imgHtml}
            <div class="game-item-info">
                <span class="game-item-name">${game.name}</span>
                ${badgeHtml}
            </div>
        `;
        item.onclick = () => {
            selectGame(game.appid, game.name);
        };
        gamesList.appendChild(item);
    });
}

function selectGame(appid, name) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'set_game_manual',
            appid: appid,
            name: name
        }));
    }
    gameModal.classList.add('hidden');
}

// ================= Background Gamepad Input Forwarding =================

function pollGamepad() {
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    let activeGamepad = null;

    for (const gp of gamepads) {
        if (gp) {
            activeGamepad = gp;
            break;
        }
    }

    if (activeGamepad && ws && ws.readyState === WebSocket.OPEN) {
        const rawButtons = activeGamepad.buttons.map(b => (typeof b === 'object' ? (b.pressed ? (b.value || 1) : 0) : b));
        const rawAxes = activeGamepad.axes.map(a => Math.abs(a) < 0.08 ? 0 : a);

        ws.send(JSON.stringify({
            type: 'input',
            state: { buttons: rawButtons, axes: rawAxes }
        }));
    }

    requestAnimationFrame(pollGamepad);
}

// ================= Init =================

window.addEventListener('DOMContentLoaded', () => {
    setupWebview();
    connectWebSocket();
    startSessionTimer();
    requestAnimationFrame(pollGamepad);
});
