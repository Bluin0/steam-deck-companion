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
const viewInputs = document.getElementById('view-inputs');
const webFrame = document.getElementById('webFrame');
const webTabTitle = document.getElementById('webTabTitle');

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
    const isNewGame = !currentGame || (game && currentGame.appid !== (game ? game.appid : null));
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

    if (currentProfile && currentProfile.tabs && !currentProfile.tabs.find(t => t.id === activeTabId)) {
        switchTab('overview');
    } else if (isNewGame && activeTabId !== 'overview' && activeTabId !== 'notes') {
        // Automatically update current web view to the new game!
        switchTab(activeTabId, true);
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

const KNOWN_MAPS = {
    'cyberpunk-2077': 'https://mapgenie.io/cyberpunk-2077/maps/night-city',
    'elden-ring': 'https://mapgenie.io/elden-ring/maps/the-lands-between',
    'grand-theft-auto-v': 'https://mapgenie.io/grand-theft-auto-v/maps/los-santos',
    'gta-v': 'https://mapgenie.io/grand-theft-auto-v/maps/los-santos',
    'red-dead-redemption-2': 'https://mapgenie.io/red-dead-redemption-2/maps/world',
    'rdr2': 'https://mapgenie.io/red-dead-redemption-2/maps/world',
    'the-witcher-3-wild-hunt': 'https://mapgenie.io/the-witcher-3-wild-hunt/maps/velen-novigrad',
    'the-witcher-3': 'https://mapgenie.io/the-witcher-3-wild-hunt/maps/velen-novigrad',
    'skyrim': 'https://mapgenie.io/skyrim/maps/skyrim',
    'the-elder-scrolls-v-skyrim': 'https://mapgenie.io/skyrim/maps/skyrim',
    'the-elder-scrolls-v-skyrim-special-edition': 'https://mapgenie.io/skyrim/maps/skyrim',
    'fallout-4': 'https://mapgenie.io/fallout-4/maps/commonwealth',
    'fallout-new-vegas': 'https://mapgenie.io/fallout-new-vegas/maps/mojave-wasteland',
    'fallout-76': 'https://mapgenie.io/fallout-76/maps/appalachia',
    'starfield': 'https://mapgenie.io/starfield/maps/new-atlantis',
    'baldurs-gate-3': 'https://mapgenie.io/baldurs-gate-3/maps/wilderness',
    'hollow-knight': 'https://mapgenie.io/hollow-knight/maps/hallownest',
    'palworld': 'https://mapgenie.io/palworld/maps/palpagos-islands',
    'genshin-impact': 'https://mapgenie.io/genshin-impact/maps/teyvat',
    'zelda-tears-of-the-kingdom': 'https://mapgenie.io/zelda-tears-of-the-kingdom/maps/hyrule',
    'the-legend-of-zelda-tears-of-the-kingdom': 'https://mapgenie.io/zelda-tears-of-the-kingdom/maps/hyrule',
    'zelda-breath-of-the-wild': 'https://mapgenie.io/zelda-breath-of-the-wild/maps/hyrule',
    'the-legend-of-zelda-breath-of-the-wild': 'https://mapgenie.io/zelda-breath-of-the-wild/maps/hyrule',
    'assassins-creed-valhalla': 'https://mapgenie.io/assassins-creed-valhalla/maps/england',
    'dying-light-2': 'https://mapgenie.io/dying-light-2/maps/villedor',
    'dying-light-2-stay-human': 'https://mapgenie.io/dying-light-2/maps/villedor',
    'horizon-forbidden-west': 'https://mapgenie.io/horizon-forbidden-west/maps/forbidden-west',
    'horizon-zero-dawn': 'https://mapgenie.io/horizon-zero-dawn/maps/world',
    'ghost-of-tsushima': 'https://mapgenie.io/ghost-of-tsushima/maps/tsushima',
    'days-gone': 'https://mapgenie.io/days-gone/maps/oregon',
    'god-of-war-ragnarok': 'https://mapgenie.io/god-of-war-ragnarok/maps/midgard',
    'god-of-war': 'https://mapgenie.io/god-of-war/maps/midgard',
    'escape-from-tarkov': 'https://mapgenie.io/tarkov/maps/customs',
    'tarkov': 'https://mapgenie.io/tarkov/maps/customs',
    'dayz': 'https://mapgenie.io/dayz/maps/chernarus',
    'sons-of-the-forest': 'https://mapgenie.io/sons-of-the-forest/maps/island',
    'the-forest': 'https://mapgenie.io/the-forest/maps/island',
    'sea-of-thieves': 'https://mapgenie.io/sea-of-thieves/maps/sea-of-thieves',
    'stalker-2': 'https://mapgenie.io/stalker-2/maps/the-zone',
    'stalker-2-heart-of-chornobyl': 'https://mapgenie.io/stalker-2/maps/the-zone',
    'black-myth-wukong': 'https://mapgenie.io/black-myth-wukong/maps/black-wind-mountain',
    'no-mans-sky': 'https://mapgenie.io/no-mans-sky/maps/euclid',
    'borderlands-3': 'https://mapgenie.io/borderlands-3/maps/pandora',
    'death-stranding': 'https://mapgenie.io/death-stranding/maps/eastern-region',
    'subnautica': 'https://subnauticamap.io/'
};

function getGameSlug(name) {
    if (!name) return '';
    return name
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}

function resolveMapUrl(gameName, gameSlug) {
    if (!gameName) return 'https://mapgenie.io';
    // If exact or partial match exists in our verified interactive maps catalog:
    if (gameSlug && KNOWN_MAPS[gameSlug]) return KNOWN_MAPS[gameSlug];
    for (const [key, url] of Object.entries(KNOWN_MAPS)) {
        if (gameSlug && (gameSlug.includes(key) || key.includes(gameSlug))) {
            return url;
        }
    }
    // Fallback: Direct search so user can enter any map immediately without 404
    return `https://www.google.com/search?q=${encodeURIComponent(gameName)}+mapa+interactivo+mapgenie`;
}

function resolveGuideUrl(gameName, rawAppId, gameSlug) {
    if (!gameName && !rawAppId) return 'https://www.google.com';
    const isNumericAppId = /^\d+$/.test(rawAppId);
    if (isNumericAppId && rawAppId !== 'default') {
        return `https://steamcommunity.com/app/${rawAppId}/guides/`;
    }
    // Fallback: Direct search with Vandal/Eliteguias guides
    return `https://www.google.com/search?q=guia+vandal+${encodeURIComponent(gameName)}`;
}

function switchTab(tabId, forceReload = false) {
    activeTabId = tabId;
    renderTabs();

    const tab = currentProfile ? currentProfile.tabs.find(t => t.id === tabId) : null;
    if (!tab) return;

    // Hide all views
    if (viewOverview) viewOverview.classList.remove('active');
    if (viewWeb) viewWeb.classList.remove('active');
    if (viewNotes) viewNotes.classList.remove('active');
    if (viewInputs) viewInputs.classList.remove('active');

    if (tab.type === 'overview') {
        if (viewOverview) viewOverview.classList.add('active');
    } else if (tab.type === 'notes') {
        if (viewNotes) viewNotes.classList.add('active');
    } else if (tab.type === 'inputs') {
        if (viewInputs) viewInputs.classList.add('active');
    } else if (tab.type === 'web') {
        if (viewWeb) viewWeb.classList.add('active');
        if (webTabTitle) webTabTitle.textContent = tab.name || 'Visor Web';

        const gName = (currentGame && currentGame.name && currentGame.name !== 'Sin juego detectado') ? currentGame.name : '';
        const rawAppId = (currentGame && currentGame.appid) ? currentGame.appid : '';
        const gSlug = getGameSlug(gName);

        let resolvedUrl = tab.url || 'https://www.google.com';

        if (tab.id === 'map') {
            resolvedUrl = resolveMapUrl(gName, gSlug);
        } else if (tab.id === 'wiki') {
            resolvedUrl = resolveGuideUrl(gName, rawAppId, gSlug);
        } else if (gName || rawAppId) {
            resolvedUrl = resolvedUrl
                .replace(/\{game_name\}/g, encodeURIComponent(gName))
                .replace(/\{game_slug\}/g, encodeURIComponent(gSlug))
                .replace(/\{appid\}/g, encodeURIComponent(rawAppId));
        } else {
            if (tab.id === 'hltb') resolvedUrl = 'https://howlongtobeat.com';
            else resolvedUrl = 'https://www.google.com';
        }

        currentWebHomeUrl = resolvedUrl;

        try {
            if (forceReload || webFrame.getAttribute('src') !== resolvedUrl) {
                startWebLoading();
                if (webFrame.loadURL) {
                    webFrame.loadURL(resolvedUrl).catch((err) => {
                        if (err && err.errno !== -3 && err.code !== 'ERR_ABORTED') {
                            console.warn('[WebView] Navigation:', err);
                        }
                    });
                } else {
                    webFrame.setAttribute('src', resolvedUrl);
                }
            }
        } catch (err) {
            webFrame.setAttribute('src', resolvedUrl);
        }
    }
}

// Webview Controls
const btnWebBack = document.getElementById('btnWebBack');
const btnWebForward = document.getElementById('btnWebForward');
const btnWebReload = document.getElementById('btnWebReload');
const btnWebHome = document.getElementById('btnWebHome');
const btnWebZoomIn = document.getElementById('btnWebZoomIn');
const btnWebZoomOut = document.getElementById('btnWebZoomOut');
const btnWebZoomReset = document.getElementById('btnWebZoomReset');
const webviewProgressBar = document.getElementById('webviewProgressBar');
const webviewSpinner = document.getElementById('webviewSpinner');

let progressTimer = null;
let safetyHideTimer = null;

function startWebLoading() {
    if (webviewSpinner) webviewSpinner.classList.remove('hidden');
    if (webviewProgressBar) {
        webviewProgressBar.classList.remove('done');
        webviewProgressBar.classList.add('loading');
        webviewProgressBar.style.width = '35%';
        if (progressTimer) clearTimeout(progressTimer);
        progressTimer = setTimeout(() => {
            if (webviewProgressBar) webviewProgressBar.style.width = '80%';
        }, 180);
    }

    // Safety timeout: dismiss after 1.8s so it never gets stuck
    if (safetyHideTimer) clearTimeout(safetyHideTimer);
    safetyHideTimer = setTimeout(stopWebLoading, 1800);
}

function stopWebLoading() {
    if (progressTimer) clearTimeout(progressTimer);
    if (safetyHideTimer) clearTimeout(safetyHideTimer);
    if (webviewSpinner) webviewSpinner.classList.add('hidden');
    if (webviewProgressBar) {
        webviewProgressBar.style.width = '100%';
        webviewProgressBar.classList.add('done');
        setTimeout(() => {
            webviewProgressBar.classList.remove('loading', 'done');
            webviewProgressBar.style.width = '0%';
        }, 350);
    }
}

// ================= Native WebView Setup =================

function setupWebview() {
    if (!webFrame) return;

    webFrame.addEventListener('did-start-loading', startWebLoading);
    webFrame.addEventListener('dom-ready', stopWebLoading);
    webFrame.addEventListener('did-stop-loading', stopWebLoading);
    webFrame.addEventListener('did-finish-load', stopWebLoading);
    webFrame.addEventListener('did-fail-load', (e) => {
        stopWebLoading();
        if (e.errorCode !== -3) {
            console.warn('[WebView] Load warning:', e);
        }
    });

    // Auto-Recovery on 404 Not Found
    webFrame.addEventListener('did-navigate', () => {
        setTimeout(() => {
            if (!webFrame) return;
            const title = (webFrame.getTitle ? webFrame.getTitle() : '').toLowerCase();
            const currentUrl = (webFrame.getURL ? webFrame.getURL() : '').toLowerCase();

            if (title.includes('404') || title.includes('not found') || currentUrl.includes('/404')) {
                const gName = (currentGame && currentGame.name && currentGame.name !== 'Sin juego detectado') ? currentGame.name : '';
                if (gName) {
                    if (activeTabId === 'map') {
                        webFrame.loadURL(`https://www.google.com/search?q=${encodeURIComponent(gName)}+mapa+interactivo+mapgenie`);
                    } else if (activeTabId === 'wiki') {
                        webFrame.loadURL(`https://www.google.com/search?q=guia+vandal+${encodeURIComponent(gName)}`);
                    }
                }
            }
        }, 400);
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

if (btnWebZoomReset) {
    btnWebZoomReset.addEventListener('click', () => {
        if (webFrame) {
            currentZoomFactor = 1.0;
            webFrame.setZoomFactor(1.0);
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

// ================= Inputs Visualizer =================

const dotLS = document.getElementById('dotLS');
const dotRS = document.getElementById('dotRS');
const valLS = document.getElementById('valLS');
const valRS = document.getElementById('valRS');
const barLT = document.getElementById('barLT');
const barRT = document.getElementById('barRT');
const valLT = document.getElementById('valLT');
const valRT = document.getElementById('valRT');
const gpStatusText = document.getElementById('gpStatusText');
const gpNameText = document.getElementById('gpNameText');

const inputBtnMap = {
    0: document.getElementById('btnA'),
    1: document.getElementById('btnB'),
    2: document.getElementById('btnX'),
    3: document.getElementById('btnY'),
    4: document.getElementById('btnLB'),
    5: document.getElementById('btnRB'),
    8: document.getElementById('btnBack'),
    9: document.getElementById('btnStart'),
    10: document.getElementById('btnL3'),
    11: document.getElementById('btnR3'),
    12: document.getElementById('btnDpadUp'),
    13: document.getElementById('btnDpadDown'),
    14: document.getElementById('btnDpadLeft'),
    15: document.getElementById('btnDpadRight')
};

function updateInputsVisualizer(gp) {
    if (!gp) return;

    if (gpStatusText) gpStatusText.textContent = 'Mando Conectado ✓';
    if (gpNameText) gpNameText.textContent = gp.id ? gp.id.substring(0, 30) : 'Gamepad';

    // Buttons
    for (let i = 0; i < gp.buttons.length; i++) {
        const el = inputBtnMap[i];
        if (el) {
            const isPressed = typeof gp.buttons[i] === 'object' ? gp.buttons[i].pressed : gp.buttons[i] > 0.5;
            if (isPressed) {
                el.classList.add('pressed');
            } else {
                el.classList.remove('pressed');
            }
        }
    }

    // Triggers (6: LT, 7: RT)
    if (gp.buttons[6] && barLT && valLT) {
        const ltVal = typeof gp.buttons[6] === 'object' ? gp.buttons[6].value : gp.buttons[6];
        const ltPct = Math.round(ltVal * 100);
        barLT.style.width = ltPct + '%';
        valLT.textContent = ltPct + '%';
    }

    if (gp.buttons[7] && barRT && valRT) {
        const rtVal = typeof gp.buttons[7] === 'object' ? gp.buttons[7].value : gp.buttons[7];
        const rtPct = Math.round(rtVal * 100);
        barRT.style.width = rtPct + '%';
        valRT.textContent = rtPct + '%';
    }

    // Joysticks
    if (gp.axes.length >= 4) {
        const lx = gp.axes[0];
        const ly = gp.axes[1];
        const rx = gp.axes[2];
        const ry = gp.axes[3];

        if (dotLS) dotLS.style.transform = `translate(${lx * 30}px, ${ly * 30}px)`;
        if (valLS) valLS.textContent = `X: ${lx.toFixed(2)} | Y: ${ly.toFixed(2)}`;

        if (dotRS) dotRS.style.transform = `translate(${rx * 30}px, ${ry * 30}px)`;
        if (valRS) valRS.textContent = `X: ${rx.toFixed(2)} | Y: ${ry.toFixed(2)}`;
    }
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

    if (activeGamepad) {
        if (activeTabId === 'inputs') {
            updateInputsVisualizer(activeGamepad);
        }

        if (ws && ws.readyState === WebSocket.OPEN) {
            const rawButtons = activeGamepad.buttons.map(b => (typeof b === 'object' ? (b.pressed ? (b.value || 1) : 0) : b));
            const rawAxes = activeGamepad.axes.map(a => Math.abs(a) < 0.08 ? 0 : a);

            ws.send(JSON.stringify({
                type: 'input',
                state: { buttons: rawButtons, axes: rawAxes }
            }));
        }
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
