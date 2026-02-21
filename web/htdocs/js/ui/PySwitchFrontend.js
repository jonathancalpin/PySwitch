/**
 * Implements the PySwitch frontend (switches, LEDs etc.)
 */
class PySwitchFrontend {
    
    #controller = null;
    #options = null;
    #container = null;
    #elementsToHide = [];    // Elements to be removed on reset

    parserFrontend = null;

    /**
     * {
     *      domNamespace,
     *      globalContainer:   Container for additional inputs (see Device.isAdditionalInput())
     * }
     */
    constructor(controller, container, options) {
        this.#controller = controller;
        this.#container = container;
        this.#options = options;    
    }

    /**
     * Remove all controls and the display (to signal that a new UI is coming up)
     */
    reset() {
        for (const item of this.#elementsToHide) {
            item.hide();
        }
    }

    /**
     * Initialize to a given set of inputs and splashes
     */
    async apply(parser) {
        if (this.parserFrontend) {
            await this.parserFrontend.destroy();
            this.parserFrontend = null;
        }

        const device = await parser.device();
        this.#container[0].className = device.getDeviceClass();

        // Clear contents and create container
        this.#container.empty();
        this.#elementsToHide = [];
        this.#options.globalContainer.empty();
        
        this.#container.append(
            $('<img id="' + this.#options.domNamespace + '-background" />')
        );

        // Create parser frontend
        this.parserFrontend = new ParserFrontend(this.#controller, parser);

        // Add switches and LEDs etc.
        await this.#initInputs(parser);

        let canvasElement = null;
        const that = this;
        this.#container.append(
            canvasElement = $('<canvas id="' + this.#options.domNamespace + '-display" />')
            .on('click', async function() {
                await that.parserFrontend.showDisplayEditor();
            })
        );
        this.#elementsToHide.push(canvasElement);
    }

    /**
     * Creates DOM elements for all inputs and LEDs.
     */
    async #initInputs(parser) {
        const hw = await parser.getHardwareInfo();
        
        // Create container for all inputs
        const inputsContainer = $('<div id="' + this.#options.domNamespace + '-inputs" />');
        this.#container.append(inputsContainer);

        // Create additional DOM items, depending on the device
        inputsContainer.append(
            await (await Device.getInstance(parser.config)).createAdditionalInputs(this.#controller)
        );
        
        // Create all inputs
        for (const inputDefinition of hw) {
            await this.#createInput(parser, inputsContainer, inputDefinition)            
        }

        // Init all frontend inputs
        await this.parserFrontend.init();
    }

    /**
     * Crate one input from a HW definition
     */
    async #createInput(parser, inputsContainer, inputDefinition) {
        const model = inputDefinition.data.model;
        const device = await parser.device();

        let visualElement = null;
        let inputElement = null;

        const isAdditional = device.isAdditionalInput(model);
        const container = isAdditional ? this.#options.globalContainer : inputsContainer;
        
        const that = this;

        switch (model.type) {
            case "AdafruitSwitch":
                container.append(
                    // Switch element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-switch-gp' + model.port + '" />')
                    .addClass(this.#options.domNamespace + '-switch')
                    .append(
                        // Headline (additional inputs only)
                        !isAdditional ? null : 
                        $('<div class="input-name" />')
                        .text(inputDefinition.displayName),

                        // Visual switch parts (LEDs)
                        visualElement = $('<div />')
                        .addClass(this.#options.domNamespace + '-switch-visual'),

                        // Overlay for hover effects and click handlers
                        $('<div />')
                        .addClass(this.#options.domNamespace + '-switch-overlay')
                        .on('mousedown touchstart', async function(e) {
                            e.currentTarget.parentNode.dataset.pushed = true;

                            if (that.#controller.ui.midiMonitor) {
                                that.#controller.ui.midiMonitor.addComment("Switch " + inputDefinition.name + " pushed");
                            }
                        })
                        .on('mouseup mouseout mouseleave touchend', async function(e) {
                            if ((e.type == "mouseup" || e.type == "touchend") && e.currentTarget.parentNode.dataset.pushed && that.#controller.ui.midiMonitor) {
                                that.#controller.ui.midiMonitor.addComment("Switch " + inputDefinition.name + " released");
                            }

                            e.currentTarget.parentNode.dataset.pushed = false;
                        })
                    )
                );
                break;

            case "AdafruitPotentiometer":
                container.append(
                    // Continuous input element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-potentiometer-gp' + model.port + '" data-value="0" />')
                    .addClass(this.#options.domNamespace + '-potentiometer')
                    .append(
                        // Headline (additional inputs only)
                        !isAdditional ? null : 
                        $('<div class="input-name" />')
                        .text(inputDefinition.displayName),
                        
                        visualElement = $('<input type="range" min="0" max="65535" value="0" />')
                        .addClass(this.#options.domNamespace + '-potentiometer-visual')
                        .on('input', async function(e) {
                            e.currentTarget.parentNode.dataset.value = $(this).val();
                        })
                    )
                );
                break;

            case "AdafruitEncoder":
                container.append(
                    // Rotary encoder element
                    inputElement = $('<div id="' + this.#options.domNamespace + '-encoder-gp' + model.port + '" data-position="0"/>')
                    .addClass(this.#options.domNamespace + '-encoder')
                    .append(
                        // Headline (additional inputs only)
                        !isAdditional ? null : 
                        $('<div class="input-name" />')
                        .text(inputDefinition.displayName),
                        
                        visualElement = $('<wc-rotation-input trigger="manipulate" displayvalue="true" />').append(
                            $('<input type="number" >')
                            .on('input', async function(e) {
                                e.currentTarget.parentNode.parentNode.dataset.position = $(this).val();
                            })
                        )
                        .addClass(this.#options.domNamespace + '-encoder-visual')                                                
                    )
                );
                break;

            // default:
            //     throw new Error("Input type unknown: " + model.type);
        }

        // LEDs (can be added to any type, theoretically)
        if (inputDefinition.data.pixels) {
            const pixels = inputDefinition.data.pixels.toSorted((a, b) => parseInt(a) - parseInt(b));
            
            for (const pixel of pixels) {
                visualElement.append(
                    $('<div id="' + this.#options.domNamespace + '-led-' + pixel + '"/>')
                    .addClass(this.#options.domNamespace + "-led")
                )
            }

            // Apply color ring from config (first action or first page color)
            if (visualElement && model.type === "AdafruitSwitch") {
                try {
                    const input = await parser.input(model.port);
                    let color = await this.#getInputDisplayColor(parser, input);
                    if (!color) {
                        color = await this.#getFallbackRingColor(parser);
                    }
                    if (color) {
                        const cssColor = color.indexOf('(') === 0 ? 'rgb' + color : 'rgb(' + color + ')';
                        visualElement.find('.' + this.#options.domNamespace + '-led')
                            .css('background-color', cssColor);
                    }
                } catch (e) {
                    // Ignore if parser input or color resolution fails
                }
            }
        }

        if (visualElement) {
            this.#elementsToHide.push(visualElement);
        }

        // Parser frontend
        await this.parserFrontend.addInput(inputDefinition, inputElement);
    }

    /**
     * Returns resolved CSS-friendly color for an input's LEDs (first action or first page color).
     * @returns {Promise<string|null>} e.g. "(r, g, b)" or null
     */
    async #getInputDisplayColor(parser, input) {
        if (!input) return null;
        const actions = input.actions(false);
        if (!actions || !actions.length) return null;

        for (const action of actions) {
            const pager = action.pager();
            const page = action.page();
            if (pager && page) {
                const pagerAction = await parser.getPagerAction(pager);
                if (pagerAction) {
                    const pages = pagerAction.argument("pages");
                    if (pages && Array.isArray(pages)) {
                        const pageProxy = pages.find((p) => p.id === page);
                        if (pageProxy && pageProxy.color) {
                            return await parser.resolveColor(pageProxy.color);
                        }
                    }
                }
            }
            const colorArg = action.argument("color");
            if (colorArg && colorArg !== "None") {
                return await parser.resolveColor(colorArg);
            }
        }
        return null;
    }

    /**
     * Fallback ring color when per-input color is not found (e.g. first page color or dim neutral).
     * @returns {Promise<string|null>} e.g. "(r, g, b)" or null
     */
    async #getFallbackRingColor(parser) {
        try {
            const pagers = await parser.actions("PagerAction");
            if (pagers && pagers.length) {
                const pages = pagers[0].argument("pages");
                if (pages && Array.isArray(pages) && pages.length && pages[0].color) {
                    return await parser.resolveColor(pages[0].color);
                }
            }
        } catch (e) { /* ignore */ }
        return "(80, 80, 80)"; // dim grey so rings are visible
    }
}