/**
 * Steam Deck Companion — Touch Dashboard Client
 */

const WS_PORT = 8765;
const wsUrl = `ws://${window.location.hostname}:${WS_PORT}`;

// State
let ws = null;
let currentGame = null;
let currentProfile = null;
let installedGames = [];
let sessionStartTime = Date.now();
let timerInterval = null;
let notesSaveTimeout = null;
let activeTabId = 'overview';

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
const iframeLoader = document.getElementById('iframeLoader');

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
        console.log('[WS] Connected to server:', wsUrl);
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

    // Switch to Overview or keep active tab if exists
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

        if (currentGame.appid && currentGame.appid !== 'default') {
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
        overviewSubtitle.textContent = 'Inicia un juego en el PC o elígelo manualmente con el botón "Juegos".';
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
        if (webFrame.src !== tab.url) {
            iframeLoader.classList.add('active');
            webFrame.src = tab.url;
            webFrame.onload = () => {
                iframeLoader.classList.remove('active');
            };
        }
    }
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
cardQuickHltb.addEventListener('click', () => switchTab('hltb'));
cardQuickNotes.addEventListener('click', () => switchTab('notes'));

// ================= Game Selector Modal =================

btnOpenPicker.addEventListener('click', () => {
    renderModalGames(installedGames);
    gameModal.classList.remove('hidden');
    gameSearchInput.value = '';
    gameSearchInput.focus();
});

btnCloseModal.addEventListener('click', () => {
    gameModal.classList.add('hidden');
});

gameSearchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = installedGames.filter(g => g.name.toLowerCase().includes(query));
    renderModalGames(filtered);
});

function renderModalGames(list) {
    gamesList.innerHTML = '';
    if (!list.length) {
        gamesList.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-secondary);">No se encontraron juegos</div>';
        return;
    }

    list.forEach(game => {
        const item = document.createElement('div');
        item.className = 'game-item';
        item.innerHTML = `
            <span class="game-item-icon">🎮</span>
            <span class="game-item-name">${game.name}</span>
        `;
        item.onclick = () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'set_game_manual',
                    appid: game.appid,
                    name: game.name
                }));
            }
            gameModal.classList.add('hidden');
        };
        gamesList.appendChild(item);
    });
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
    connectWebSocket();
    startSessionTimer();
    requestAnimationFrame(pollGamepad);
});
