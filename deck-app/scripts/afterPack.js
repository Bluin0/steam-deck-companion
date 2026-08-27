const fs = require('fs');
const path = require('path');

exports.default = async function(context) {
    if (context.electronPlatformName !== 'linux') return;

    const candidates = [
        context.packager.executableName,
        'SteamDeckCompanion',
        'steam-deck-companion'
    ].filter(Boolean);

    for (const name of candidates) {
        const binPath = path.join(context.appOutDir, name);
        const realBinPath = path.join(context.appOutDir, `${name}.bin`);

        if (fs.existsSync(realBinPath)) {
            // Already wrapped
            break;
        }

        if (fs.existsSync(binPath)) {
            try {
                // Check if it's an ELF binary
                const buf = Buffer.alloc(4);
                const fd = fs.openSync(binPath, 'r');
                fs.readSync(fd, buf, 0, 4, 0);
                fs.closeSync(fd);

                if (buf[0] === 0x7f && buf[1] === 0x45 && buf[2] === 0x4c && buf[3] === 0x46) {
                    fs.renameSync(binPath, realBinPath);

                    const wrapper = `#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/${name}.bin" --no-sandbox --disable-dev-shm-usage "$@"
`;
                    fs.writeFileSync(binPath, wrapper, { mode: 0o755 });
                    fs.chmodSync(binPath, 0o755);
                    fs.chmodSync(realBinPath, 0o755);
                    console.log(`[afterPack] Injected zero-delay SteamOS wrapper for: ${name}`);
                    break;
                }
            } catch (err) {
                console.warn('[afterPack] Warning inspecting binary:', err);
            }
        }
    }
};
