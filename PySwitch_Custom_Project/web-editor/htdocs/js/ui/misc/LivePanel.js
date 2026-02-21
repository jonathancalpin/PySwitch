/**
 * Live panel next to the device: recent CC messages and tap tempo info.
 * Uses the unused third of the screen.
 */
class LivePanel {

    #container = null;
    #ccList = null;
    #tapLine = null;
    #maxCcLines = 15;
    #ccLines = [];
    #tapCcs = [85];  // CC 85 = Tap Tempo (PaintAudio); can extend

    constructor(containerElement) {
        this.#container = $(containerElement);
        this.#build();
    }

    #build() {
        this.#container.empty().append(
            $('<div class="live-panel-section"/>').append(
                $('<h3/>').text('Page (bank)'),
                $('<div class="live-panel-combo"/>').append(
                    $('<button type="button" class="live-panel-combo-btn" aria-label="Page up"/>').text('Page ↑').on('click', () => this.#simulateCombo(['pyswitch-switch-gp9', 'pyswitch-switch-gp10'])),
                    $('<button type="button" class="live-panel-combo-btn" aria-label="Page down"/>').text('Page ↓').on('click', () => this.#simulateCombo(['pyswitch-switch-gp10', 'pyswitch-switch-gp11']))
                )
            ),
            $('<div class="live-panel-section"/>').append(
                $('<h3/>').text('Combo (emulator)'),
                $('<div class="live-panel-combo"/>').append(
                    $('<button type="button" class="live-panel-combo-btn"/>').text('A+B').on('click', () => this.#simulateCombo(['pyswitch-switch-gp9', 'pyswitch-switch-gp10'])),
                    $('<button type="button" class="live-panel-combo-btn"/>').text('B+C').on('click', () => this.#simulateCombo(['pyswitch-switch-gp10', 'pyswitch-switch-gp11']))
                )
            ),
            $('<div class="live-panel-section"/>').append(
                $('<h3/>').text('CC messages'),
                this.#ccList = $('<div class="live-panel-cc"/>')
            ),
            $('<div class="live-panel-section"/>').append(
                $('<h3/>').text('Tap tempo'),
                this.#tapLine = $('<div class="live-panel-tap"/>').append(
                    $('<span class="tap-value"/>').text('—')
                )
            )
        );
    }

    /**
     * Simulate a combo press in the emulator: set pushed on the given switch IDs, then release after a short delay.
     * @param {string[]} switchIds - e.g. ['pyswitch-switch-gp9', 'pyswitch-switch-gp10']
     */
    #simulateCombo(switchIds) {
        const elements = switchIds.map(id => document.getElementById(id)).filter(Boolean);
        if (elements.length === 0) return;
        elements.forEach(el => { el.dataset.pushed = 'true'; });
        setTimeout(() => {
            elements.forEach(el => { el.dataset.pushed = 'false'; });
        }, 120);
    }

    /**
     * Add a MIDI message; only CC (status 0xB0 / 176) are shown.
     * @param {Uint8Array|Array} message - raw bytes
     * @param {string} direction - "in" or "out"
     */
    addMessage(message, direction) {
        if (!message || message.length < 3) return;
        const status = message[0];
        if ((status & 0xF0) !== 0xB0) return;  // Control Change only
        const cc = message[1];
        const value = message[2];
        const dir = direction === 'out' ? 'out' : 'in';
        const line = $('<div class="cc-line cc-' + dir + '"/>').text(
            (dir === 'out' ? '→ ' : '← ') + 'CC ' + cc + ' = ' + value
        );
        this.#ccLines.push(line);
        this.#ccList.append(line);
        while (this.#ccLines.length > this.#maxCcLines) {
            this.#ccLines.shift().remove();
        }
        line[0].scrollIntoView(false);
        if (this.#tapCcs.indexOf(cc) >= 0) {
            this.setLastTap(cc, value);
        }
    }

    /**
     * Update last tap tempo display.
     * @param {number} cc - CC number (e.g. 85)
     * @param {number} value - optional value
     */
    setLastTap(cc, value) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-GB', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.#tapLine.find('.tap-value').text('Last tap: ' + timeStr + (value !== undefined ? ' (CC ' + cc + '=' + value + ')' : ''));
    }
}
