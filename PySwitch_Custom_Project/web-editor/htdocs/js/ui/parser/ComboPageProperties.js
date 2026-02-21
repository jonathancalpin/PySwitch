/**
 * ComboPageProperties.js
 * 
 * UI component for configuring combo-based page navigation.
 * Allows users to:
 * - Enable/disable combo page navigation
 * - Configure which buttons form combos (A+B, B+C)
 * - Set the combo detection window timing
 * - Manage pages (add, remove, reorder)
 */
class ComboPageProperties {
    
    #parser = null;
    #controller = null;
    #container = null;
    #pagesList = null;
    #comboConfig = null;
    #onChange = null;

    constructor(parser, controller, onChange) {
        this.#parser = parser;
        this.#controller = controller;
        this.#onChange = onChange;
    }

    /**
     * Create the combo configuration panel
     */
    async create() {
        const that = this;
        
        // Check if this config uses combo navigation
        const hasCombo = await this.#parser.hasComboConfig();
        this.#comboConfig = await this.#parser.getComboConfig();
        
        this.#container = $('<div class="combo-page-properties" />');
        
        if (!hasCombo) {
            // Show option to enable combo navigation
            this.#container.append(
                $('<div class="combo-enable-panel" />').append(
                    $('<p />').text("This configuration uses standard PySwitch paging."),
                    $('<button class="button" />').text("Enable Combo Page Navigation")
                        .on('click', async function() {
                            await that.#enableComboNavigation();
                        })
                )
            );
        } else {
            // Show combo configuration UI
            await this.#buildComboUI();
        }
        
        return this.#container;
    }

    /**
     * Build the combo configuration UI
     */
    async #buildComboUI() {
        const that = this;
        const config = this.#comboConfig || {
            enabled: true,
            combo_switches: ['A', 'B', 'C'],
            combo_window_ms: 50
        };
        
        // Clear container
        this.#container.empty();
        
        // Header
        this.#container.append(
            $('<div class="combo-header" />').append(
                $('<h3 />').text("Combo Page Navigation"),
                $('<span class="combo-status" />')
                    .text(config.enabled ? "Enabled" : "Disabled")
                    .addClass(config.enabled ? "status-enabled" : "status-disabled")
            )
        );
        
        // Settings panel
        const settingsPanel = $('<div class="combo-settings" />');
        
        // Enable/Disable toggle
        settingsPanel.append(
            $('<div class="setting-row" />').append(
                $('<label />').text("Enable Combo Navigation"),
                $('<input type="checkbox" class="combo-enabled" />')
                    .prop('checked', config.enabled)
                    .on('change', async function() {
                        await that.#updateComboConfig('enabled', $(this).prop('checked'));
                    })
            )
        );
        
        // Combo window timing
        settingsPanel.append(
            $('<div class="setting-row" />').append(
                $('<label />').text("Combo Detection Window (ms)"),
                $('<input type="number" class="combo-window" min="20" max="200" step="10" />')
                    .val(config.combo_window_ms || 50)
                    .on('change', async function() {
                        await that.#updateComboConfig('combo_window_ms', parseInt($(this).val()));
                    }),
                $('<span class="setting-help" />').text("Time window to detect simultaneous button presses")
            )
        );
        
        // Combo switches selector
        settingsPanel.append(
            $('<div class="setting-row" />').append(
                $('<label />').text("Combo Switches"),
                $('<div class="combo-switches-selector" />').append(
                    this.#createSwitchCheckbox('A', config.combo_switches),
                    this.#createSwitchCheckbox('B', config.combo_switches),
                    this.#createSwitchCheckbox('C', config.combo_switches)
                ),
                $('<span class="setting-help" />').text("Switches that can form page navigation combos")
            )
        );
        
        // Combo assignments display (A+B = Page Up, B+C = Page Down)
        settingsPanel.append(
            $('<div class="combo-assignments" />').append(
                $('<h4 />').text("Page Navigation:"),
                $('<div class="combo-assignment" />').append(
                    $('<span class="combo-keys" />').text("A + B"),
                    $('<span class="combo-arrow" />').text("→"),
                    $('<span class="combo-action" />').text("Page Up")
                ),
                $('<div class="combo-assignment" />').append(
                    $('<span class="combo-keys" />').text("B + C"),
                    $('<span class="combo-arrow" />').text("→"),
                    $('<span class="combo-action" />').text("Page Down")
                )
            )
        );
        
        this.#container.append(settingsPanel);
        
        // Pages list
        this.#container.append(
            $('<div class="pages-section" />').append(
                $('<h3 />').text("Pages"),
                await this.#createPagesList()
            )
        );
    }

    /**
     * Create a checkbox for switch selection
     */
    #createSwitchCheckbox(switchName, selectedSwitches) {
        const that = this;
        const isSelected = selectedSwitches && selectedSwitches.includes(switchName);
        
        return $('<label class="switch-checkbox" />').append(
            $('<input type="checkbox" />')
                .prop('checked', isSelected)
                .attr('data-switch', switchName)
                .on('change', async function() {
                    await that.#updateComboSwitches();
                }),
            $('<span />').text(switchName)
        );
    }

    /**
     * Update combo switches configuration
     */
    async #updateComboSwitches() {
        const switches = [];
        this.#container.find('.combo-switches-selector input:checked').each(function() {
            switches.push($(this).attr('data-switch'));
        });
        
        await this.#updateComboConfig('combo_switches', switches);
    }

    /**
     * Update a single combo config property
     */
    async #updateComboConfig(key, value) {
        if (!this.#comboConfig) {
            this.#comboConfig = {
                enabled: true,
                combo_switches: ['A', 'B', 'C'],
                combo_window_ms: 50
            };
        }
        
        this.#comboConfig[key] = value;
        
        try {
            await this.#parser.setComboConfig(this.#comboConfig);
            
            if (this.#onChange) {
                await this.#onChange();
            }
        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Enable combo navigation for a standard config
     */
    async #enableComboNavigation() {
        const defaultConfig = {
            enabled: true,
            combo_switches: ['A', 'B', 'C'],
            combo_window_ms: 50
        };
        
        try {
            await this.#parser.setComboConfig(defaultConfig);
            this.#comboConfig = defaultConfig;
            
            // Rebuild UI
            await this.#buildComboUI();
            
            if (this.#onChange) {
                await this.#onChange();
            }
        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Create the pages list UI
     */
    async #createPagesList() {
        const that = this;
        const pages = await this.#parser.getPages();
        const pagesOrder = await this.#parser.getPagesOrder();
        
        const container = $('<div class="pages-list" />');
        
        // Create page entries in order
        for (const pageName of pagesOrder) {
            const page = pages.find(p => p.var_name === pageName);
            if (page) {
                container.append(await this.#createPageEntry(page));
            }
        }
        
        // Add new page button
        container.append(
            $('<div class="add-page-row" />').append(
                $('<button class="button add-page-btn" />').append(
                    $('<i class="fas fa-plus" />'),
                    $('<span />').text(" Add Page")
                ).on('click', async function() {
                    await that.#addNewPage();
                })
            )
        );
        
        return container;
    }

    /**
     * Create a single page entry UI
     */
    async #createPageEntry(page) {
        const that = this;
        const data = page.data || {};
        
        // Parse color theme
        let colorStyle = '';
        if (data.color_theme) {
            const color = Array.isArray(data.color_theme) 
                ? `rgb(${data.color_theme[0]}, ${data.color_theme[1]}, ${data.color_theme[2]})`
                : data.color_theme;
            colorStyle = `background-color: ${color}`;
        }
        
        return $('<div class="page-entry" />').attr('data-page', page.var_name).append(
            // Drag handle
            $('<span class="page-drag-handle fas fa-grip-vertical" />'),
            
            // Color indicator
            $('<span class="page-color-indicator" />').attr('style', colorStyle),
            
            // Page name
            $('<input type="text" class="page-name-input" placeholder="Page Name" />')
                .val(data.name || '')
                .on('change', async function() {
                    await that.#updatePageProperty(page.var_name, 'name', $(this).val());
                }),
            
            // Channel selector
            $('<select class="page-channel-select" />').append(
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16].map(ch => 
                    $('<option />').val(ch).text(`Ch ${ch}`).prop('selected', data.channel === ch)
                )
            ).on('change', async function() {
                await that.#updatePageProperty(page.var_name, 'channel', parseInt($(this).val()));
            }),
            
            // MIDI output selector
            $('<select class="page-midi-out-select" />').append(
                $('<option value="USB" />').text("USB").prop('selected', data.midi_out === 'USB'),
                $('<option value="DIN" />').text("DIN").prop('selected', data.midi_out === 'DIN')
            ).on('change', async function() {
                await that.#updatePageProperty(page.var_name, 'midi_out', $(this).val());
            }),
            
            // Color picker
            $('<input type="color" class="page-color-picker" />')
                .val(this.#rgbToHex(data.color_theme))
                .on('change', async function() {
                    const rgb = that.#hexToRgb($(this).val());
                    await that.#updatePageProperty(page.var_name, 'color_theme', rgb);
                }),
            
            // Edit switches button
            $('<button class="button page-edit-btn" title="Edit Switches" />').append(
                $('<i class="fas fa-sliders-h" />')
            ).on('click', async function() {
                await that.#editPageSwitches(page.var_name);
            }),
            
            // Remove button
            $('<button class="button page-remove-btn" title="Remove Page" />').append(
                $('<i class="fas fa-times" />')
            ).on('click', async function() {
                await that.#removePage(page.var_name);
            })
        );
    }

    /**
     * Update a page property
     */
    async #updatePageProperty(pageName, property, value) {
        try {
            const pages = await this.#parser.getPages();
            const page = pages.find(p => p.var_name === pageName);
            
            if (page && page.data) {
                page.data[property] = value;
                await this.#parser.setPage(pageName, page.data);
                
                if (this.#onChange) {
                    await this.#onChange();
                }
            }
        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Add a new page
     */
    async #addNewPage() {
        try {
            const pages = await this.#parser.getPages();
            const pageNum = pages.length + 1;
            const pageName = `PAGE_${pageNum}`;
            
            await this.#parser.createPage(pageName, `Page ${pageNum}`, 1);
            
            // Rebuild pages list
            await this.#buildComboUI();
            
            if (this.#onChange) {
                await this.#onChange();
            }
        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Remove a page
     */
    async #removePage(pageName) {
        if (!confirm(`Remove page "${pageName}"?`)) return;
        
        try {
            await this.#parser.removePage(pageName);
            
            // Rebuild pages list
            await this.#buildComboUI();
            
            if (this.#onChange) {
                await this.#onChange();
            }
        } catch (e) {
            this.#controller.handle(e);
        }
    }

    /**
     * Edit switches for a page (opens switch editor)
     */
    async #editPageSwitches(pageName) {
        // TODO: Implement switch editing UI
        // For now, show a message
        alert(`Switch editing for ${pageName} - Coming soon!\n\nFor now, edit switches in the code editor.`);
    }

    /**
     * Convert RGB array to hex color
     */
    #rgbToHex(rgb) {
        if (!rgb || !Array.isArray(rgb)) return '#ffffff';
        const r = rgb[0].toString(16).padStart(2, '0');
        const g = rgb[1].toString(16).padStart(2, '0');
        const b = rgb[2].toString(16).padStart(2, '0');
        return `#${r}${g}${b}`;
    }

    /**
     * Convert hex color to RGB array
     */
    #hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16)
        ] : [255, 255, 255];
    }
}
