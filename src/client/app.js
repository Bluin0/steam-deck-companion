/**
 * Steam Deck Companion Frontend Client Script.
 * 
 * Captures Gamepad API events and sends input state over WebSocket.
 * Listens for active game updates broadcast by the PC server.
 */

const WS_PORT = 8765;
const wsUrl = `ws://${window.location.hostname}:${WS_PORT}`;

let ws = null;
let activeGamepad = null;
let lastInputState = null;

// DOM Elements
const connBadge = document.getElementById('connBadge');
const connText = document.getElementById('connText');
const gameTitle = document.getElementById('gameTitle');
const gameSubtitle = document.getElementById('gameSubtitle');
const appIdTag = document.getElementById('appIdTag');
const pidTag = document.getElementById('pidTag');
const gpStatus = document.getElementById('gpStatus');
const leftStickDot = document.getElementById('leftStickDot');
const rightStickDot = document.getElementById('rightStickDot');
const buttonElements = document.querySelectorAll('.btn-indicator');

// Connect WebSocket
function connectWebSocket() {
    connText.textContent = 'Connecting...';
    connBadge.classList.remove('connected');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        connText.textContent = 'Connected to PC';
        connBadge.classList.add('connected');
        console.log('[WS] Connected to server:', wsUrl);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'game_update') {
                updateGameDisplay(data.game);
            }
        } catch (e) {
            console.error('[WS] Error parsing message:', e);
        }
    };

    ws.onclose = () => {
        connText.textContent = 'Disconnected (Retrying)';
        connBadge.classList.remove('connected');
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error('[WS] Error:', err);
    };
}

// Update Active Game Info UI
function updateGameDisplay(game) {
    if (!game) {
        gameTitle.textContent = 'No Game Detected';
        gameSubtitle.textContent = 'Launch a Steam game on your PC';
        appIdTag.textContent = 'AppID: --';
        pidTag.textContent = 'PID: --';
        return;
    }

    gameTitle.textContent = game.name;
    gameSubtitle.textContent = `Running executable: ${game.exe}`;
    appIdTag.textContent = `AppID: ${game.appid}`;
    pidTag.textContent = `PID: ${game.pid}`;
}

// Normalize Gamepad Input for both Standard (Steam Input) and Raw Linux Steam Deck (Steam app closed)
function normalizeGamepadInput(gp) {
    const rawButtons = gp.buttons.map(b => b.pressed ? 1 : 0);
    const rawAxes = gp.axes.map(a => Math.abs(a) < 0.08 ? 0 : a); // 0.08 deadzone

    // 1. If mapping is standard (W3C standard, e.g. Steam Input active)
    if (gp.mapping === 'standard') {
        return { buttons: rawButtons, axes: rawAxes };
    }

    // 2. Raw Linux Steam Deck (Steam app closed)
    const normalizedButtons = [...rawButtons];

    // Raw Linux Deck evdev swaps A and Y face buttons: raw[3] is A, raw[0] is Y
    if (rawButtons.length >= 4) {
        normalizedButtons[0] = rawButtons[3]; // A
        normalizedButtons[1] = rawButtons[1]; // B
        normalizedButtons[2] = rawButtons[2]; // X
        normalizedButtons[3] = rawButtons[0]; // Y
    }

    // Raw evdev layout: axes[0]=LX, axes[1]=LY, axes[2]=LT, axes[3]=RX, axes[4]=RY, axes[5]=RT, axes[6]=DpadX, axes[7]=DpadY
    const normalizedAxes = [0, 0, 0, 0];

    if (rawAxes.length >= 5) {
        normalizedAxes[0] = rawAxes[0]; // LX
        normalizedAxes[1] = rawAxes[1]; // LY
        normalizedAxes[2] = rawAxes[3]; // RX (Skip LT at index 2)
        normalizedAxes[3] = rawAxes[4]; // RY
    } else {
        normalizedAxes[0] = rawAxes[0] || 0;
        normalizedAxes[1] = rawAxes[1] || 0;
        normalizedAxes[2] = rawAxes[2] || 0;
        normalizedAxes[3] = rawAxes[3] || 0;
    }

    // D-Pad Hat axes mapping (axes[6] & axes[7])
    if (rawAxes.length >= 8) {
        if (rawAxes[6] < -0.5) normalizedButtons[14] = 1; // Left
        if (rawAxes[6] > 0.5)  normalizedButtons[15] = 1; // Right
        if (rawAxes[7] < -0.5) normalizedButtons[12] = 1; // Up
        if (rawAxes[7] > 0.5)  normalizedButtons[13] = 1; // Down
    }

    return { buttons: normalizedButtons, axes: normalizedAxes };
}

// Poll Gamepad API
function pollGamepad() {
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    activeGamepad = null;

    for (const gp of gamepads) {
        if (gp) {
            activeGamepad = gp;
            break;
        }
    }

    if (!activeGamepad) {
        gpStatus.textContent = 'No Controller Detected (Press any button)';
        requestAnimationFrame(pollGamepad);
        return;
    }

    gpStatus.textContent = `Controller Active: ${activeGamepad.id.substring(0, 24)}... (${activeGamepad.mapping || 'raw'})`;

    // Process buttons & axes with auto-normalization
    const { buttons, axes } = normalizeGamepadInput(activeGamepad);

    // Update Visual HUD
    updateGamepadHUD(buttons, axes);

    // Send state over WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        const inputState = { buttons, axes };
        ws.send(JSON.stringify({
            type: 'input',
            state: inputState
        }));
    }

    requestAnimationFrame(pollGamepad);
}

function updateGamepadHUD(buttons, axes) {
    // Update button elements
    buttonElements.forEach(el => {
        const btnIndex = parseInt(el.getAttribute('data-btn'), 10);
        if (buttons[btnIndex]) {
            el.classList.add('pressed');
        } else {
            el.classList.remove('pressed');
        }
    });

    // Update sticks visual
    if (axes.length >= 4) {
        const lx = axes[0] * 35;
        const ly = axes[1] * 35;
        leftStickDot.style.transform = `translate(${lx}px, ${ly}px)`;

        const rx = axes[2] * 35;
        const ry = axes[3] * 35;
        rightStickDot.style.transform = `translate(${rx}px, ${ry}px)`;
    }
}

// Window Event Listeners
window.addEventListener('gamepadconnected', (e) => {
    console.log('[Gamepad] Connected:', e.gamepad.id);
});

window.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    requestAnimationFrame(pollGamepad);
});
