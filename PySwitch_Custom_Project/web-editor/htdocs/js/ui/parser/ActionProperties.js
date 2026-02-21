/**
 * Parse CUSTOM_MESSAGE message value to simple fields (CC or PC).
 * @param {string} value - e.g. "[176, 80, 127]" or "[0xB0, 80, 0]"
 * @returns {{ type: 'cc'|'pc'|'raw', channel?: number, cc?: number, valueOn?: number, valueOff?: number, pc?: number }}
 */
function parseCustomMessage(value) {
    if (value === null || value === undefined || value === "None") return { type: "raw" };
    let arr = null;
    if (typeof value === "string") {
        try {
            arr = JSON.parse(value.replace(/\b0x([0-9a-fA-F]+)\b/g, (_, hex) => parseInt(hex, 16)));
        } catch (_) {
            const ccMatch = value.match(/\[\s*0xB0\s*\+\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]/i);
            if (ccMatch) {
                return { type: "cc", channel: parseInt(ccMatch[1], 10) + 1, cc: parseInt(ccMatch[2], 10), valueOn: parseInt(ccMatch[3], 10), valueOff: 0 };
            }
            const pcMatch = value.match(/\[\s*0xC0\s*\+\s*(\d+)\s*,\s*(\d+)\s*\]/i);
            if (pcMatch) {
                return { type: "pc", channel: parseInt(pcMatch[1], 10) + 1, pc: parseInt(pcMatch[2], 10) };
            }
            return { type: "raw" };
        }
    } else if (Array.isArray(value)) {
        arr = value;
    }
    if (!arr || arr.length < 2) return { type: "raw" };
    const status = arr[0] & 0xF0;
    const ch = (arr[0] & 0x0F) + 1;
    if (status === 0xB0 && arr.length >= 3) {
        return { type: "cc", channel: ch, cc: arr[1], valueOn: arr[2], valueOff: 0 };
    }
    if (status === 0xC0 && arr.length >= 2) {
        return { type: "pc", channel: ch, pc: arr[1] };
    }
    return { type: "raw" };
}

/**
 * Build message / message_release for CUSTOM_MESSAGE from simple fields.
 * @param {string} type - 'cc' or 'pc'
 * @param {{ channel: number, cc?: number, valueOn?: number, valueOff?: number, pc?: number }} opts
 * @returns {{ message: string, message_release: string|null }}
 */
function buildCustomMessage(type, opts) {
    const ch = Math.max(1, Math.min(16, (opts.channel || 1))) - 1;
    if (type === "cc") {
        const cc = Math.max(0, Math.min(127, opts.cc ?? 0));
        const on = Math.max(0, Math.min(127, opts.valueOn ?? 127));
        const off = Math.max(0, Math.min(127, opts.valueOff ?? 0));
        return {
            message: "[0xB0 + " + ch + ", " + cc + ", " + on + "]",
            message_release: "[0xB0 + " + ch + ", " + cc + ", " + off + "]"
        };
    }
    if (type === "pc") {
        const pc = Math.max(0, Math.min(127, opts.pc ?? 0));
        return {
            message: "[0xC0 + " + ch + ", " + pc + "]",
            message_release: "None"
        };
    }
    return { message: null, message_release: null };
}

/**
 * Implements the parameter editor
 */
class ActionProperties {
    
    actionDefinition = null;
    inputs = null;
    parserFrontend = null;
    controller = null;
    oldProperties = null;

    #messages = null;
    #pagers = null;
    #internalRows = null;
    #encoderProps = null;
    #advancedRows = null;
    #advancedLevel = 0;
    #customMessageRawRows = [];

    constructor(controller, parserFrontend, actionDefinition, oldProperties = null, messages = []) {
        this.controller = controller;
        this.parserFrontend = parserFrontend;
        this.actionDefinition = actionDefinition;
        
        this.oldProperties = oldProperties;
        this.#messages = messages;
        
        this.#pagers = new PagerProperties(this);
        this.#internalRows = new ActionPropertiesInternal(this);
        this.#encoderProps = new ActionPropertiesEncoder(this);
    }

    /**
     * Initialize after adding to DOM
     */
    async init() {
        await this.#pagers.init();
        await this.update();
    }

    /**
     * Generate the DOM for the properties panel
     */
    async get() {
        this.#advancedRows = [];
        this.#customMessageRawRows = [];
        this.inputs = new Map();

        /**
         * Take over old values from the old props object, if different from the default
         */
        async function takeOverValues(input, param) {
            if (param.meta.type() == "text") return;
            if (!that.oldProperties) return;
                
            const oldParam = that.oldProperties.getParameterDefinition(param.name);
            const oldValue = that.oldProperties.getParameterValue(param.name);
            
            if (oldValue !== null && oldValue != oldParam.meta.getDefaultValue()) {
                await that.#setInputValue(input, param, oldValue);
            }
        }

        /**
         * Returns the passed element with the passed comment on hover
         */
        function withComment(el, param, comment) {
            if (param && param.meta.data.hideComment) return el;

            return Tools.withComment(el, comment)
        }

        const that = this;
        const isCustomMessage = this.actionDefinition.name === "CUSTOM_MESSAGE";
        const customMessageSimpleRows = isCustomMessage ? await this.#getCustomMessageSimpleRows() : [];


        const parameters = await Promise.all(
            this.actionDefinition.parameters
            .sort(function(a, b) {
                return (a.meta.data.advanced ? a.meta.data.advanced : 0) - (b.meta.data.advanced ? b.meta.data.advanced : 0);
            })
            .map(
                async (param) => {
                    const input = await this.#createInput(param);

                    that.inputs.set(param.name, input);

                    // Take over old values from the old props object, if different from the default
                    await takeOverValues(input, param);

                    const messages = that.#messages.filter((item) => item.parameter == param.name);
                    const hideInSimple = isCustomMessage && ["message", "message_release", "text", "color", "toggle", "group"].includes(param.name);

                    const row = withComment(
                        $('<tr class="selectable" />')
                            .addClass(hideInSimple ? "custom-message-simple-hidden" : "")
                            .append(
                                $('<td />').append(
                                    $('<span />').text(param.meta.getDisplayName())
                                ),
                                $('<td />')
                                    .addClass(messages.length ? "has-messages" : null)
                                    .append(
                                        input,
                                        ...(await that.#createAdditionalInputOptions(input, param))
                                    )
                            ),
                        param,
                        await this.#getParameterComment(param)
                    );

                    if (hideInSimple) that.#customMessageRawRows.push(row);

                    if (!messages.length) {
                        if (param.meta.data.advanced) {
                            that.registerAdvancedParameterRow(row, param);
                        }
                        return row;
                    } else {
                        const msgRows = messages.map((item) =>
                            $('<tr class="param-messages" />').append(
                                $('<td />'),
                                $('<td />').append(item.message)
                            )
                        );
                        if (hideInSimple) msgRows.forEach((r) => that.#customMessageRawRows.push(r));
                        return [row, ...msgRows];
                    }
                }
            )
        );
        
        // Internal parameters (assign, hold etc.)
        const internalRows = [].concat(
            (await this.#internalRows.get()),
            (await this.#pagers.get())            
        )
        .map(
            (item) => {
                return item ? withComment(
                    item.element,
                    null,
                    item.comment
                ) : null;
            }
        );

        let tbody = null;
        const ret = $('<div class="action-properties" />').append(
            // Action name
            $('<div class="action-header" />')
            .text(this.actionDefinition.meta.getDisplayName()),
            
            // Comment
            $('<div class="action-comment" />')
            .html(this.#getActionComment()),

            // Parameters
            $('<div class="action-header" />')
            .text("Parameters:"),

            $('<div class="action-parameters" />').append(
                $('<table />').append(
                    tbody = $('<tbody />').append(
                        ...internalRows,
                        ...customMessageSimpleRows,
                        parameters.flat()
                    )
                )
            ),

            // Pager buttons
            ...(await this.#pagers.getButtons())
        );

        await this.#internalRows.setup();
        await this.#pagers.setup();
        await this.#encoderProps.setup();

        // Advanced parameters: Show all button
        if (this.#advancedRows.length > 0) {
            let advRow = null;
            tbody.append(
                advRow = $('<tr />').append(
                    $('<td colspan="2" />').append(
                        $('<span class="show-advanced" />')
                        .text("more...")
                        .on('click', async function() {
                            try {
                                that.#advancedLevel++;
                                that.#updateAdvancedLevel(advRow);
                                
                            } catch (e) {
                                that.controller.handle(e);
                            }
                        })
                    )
                )
            )
        }

        return ret;
    }

    /**
     * Adds an advanced parameter row to an array to show them later (the array is 2 dimensional, grouped by advanced value)
     */
    registerAdvancedParameterRow(row, param) {
        row.hide();

        const level = param.meta.data.advanced;

        // Check if level exists
        while (this.#advancedRows.length < level) {
            this.#advancedRows.push([]);
        }

        this.#advancedRows[level - 1].push(
            {
                row: row,
                parameterName: param.name
            }
        );
    }

    /**
     * Update advanced parameter rows to the currend advancedLevel.
     */
    #updateAdvancedLevel(advRow) {
        if (this.#advancedRows.length < this.#advancedLevel) return;
                                
        for (const row of this.#advancedRows[this.#advancedLevel - 1]) {
            row.row.show();
        }

        if (this.#advancedRows.length == this.#advancedLevel + 1) {
            advRow.find('.show-advanced').text("all...");
        }

        if (this.#advancedRows.length == this.#advancedLevel) {
            // Last level
            advRow.hide();
        }
    }

    /**
     * Build simple-edit rows for CUSTOM_MESSAGE (CC/PC channel, control, value, toggle, label, color).
     * @returns {Promise<JQuery[]>}
     */
    async #getCustomMessageSimpleRows() {
        const that = this;
        const msgVal = this.oldProperties ? this.oldProperties.getParameterValue("message") : "[176, 80, 127]";
        const msgRelVal = this.oldProperties ? this.oldProperties.getParameterValue("message_release") : "None";
        const toggleVal = this.oldProperties ? this.oldProperties.getParameterValue("toggle") : "False";
        const groupVal = this.oldProperties ? this.oldProperties.getParameterValue("group") : "None";
        const textVal = this.oldProperties ? this.oldProperties.getParameterValue("text") : "";
        const colorVal = this.oldProperties ? this.oldProperties.getParameterValue("color") : "Colors.WHITE";

        const parsed = parseCustomMessage(msgVal);
        let valueOff = 0;
        if (parsed.type === "cc" && msgRelVal && msgRelVal !== "None") {
            try {
                const arr = typeof msgRelVal === "string" ? JSON.parse(msgRelVal.replace(/\b0x([0-9a-fA-F]+)\b/g, (_, h) => parseInt(h, 16))) : msgRelVal;
                if (arr && arr.length >= 3) valueOff = arr[2];
            } catch (_) {}
        }

        const typeSelect = $('<select />')
            .append(
                $('<option value="cc" />').text("Control Change (CC)"),
                $('<option value="pc" />').text("Program Change (PC)"),
                $('<option value="raw" />').text("Raw MIDI bytes")
            )
            .val(parsed.type === "raw" ? "raw" : parsed.type);
        this.inputs.set("_midiType", typeSelect);

        const channelInput = $('<input type="number" min="1" max="16" />').val(parsed.channel || 1);
        this.inputs.set("_channel", channelInput);

        const ccInput = $('<input type="number" min="0" max="127" />').val(parsed.cc ?? 80);
        this.inputs.set("_cc", ccInput);

        const valueOnInput = $('<input type="number" min="0" max="127" />').val(parsed.valueOn ?? 127);
        this.inputs.set("_valueOn", valueOnInput);

        const valueOffInput = $('<input type="number" min="0" max="127" />').val(parsed.type === "cc" ? valueOff : 0);
        this.inputs.set("_valueOff", valueOffInput);

        const pcInput = $('<input type="number" min="0" max="127" />').val(parsed.pc ?? 0);
        this.inputs.set("_pc", pcInput);

        const labelInput = $('<input type="text" />').val(typeof textVal === "string" ? textVal.replace(/^["']|["']$/g, "") : "");
        this.inputs.set("_simpleLabel", labelInput);

        const toggleCheck = $('<input type="checkbox" />').prop("checked", toggleVal === "True");
        this.inputs.set("_simpleToggle", toggleCheck);

        const groupInput = $('<input type="text" placeholder="e.g. pc_ch1" />').val(groupVal && groupVal !== "None" ? groupVal.replace(/^["']|["']$/g, "") : "");
        this.inputs.set("_simpleGroup", groupInput);

        const colors = await this.parserFrontend.parser.getAvailableColors();
        const colorSelect = $('<select />')
            .append(
                (colors || []).map((c) => $('<option value="' + c.name + '" />').text(c.name)),
                $('<option value="">Custom...</option>')
            )
            .val(typeof colorVal === "string" && colorVal.startsWith("Colors.") ? colorVal : "Colors.WHITE");
        this.inputs.set("_simpleColor", colorSelect);

        function updateVisibility() {
            const t = typeSelect.val();
            const table = typeSelect.closest("table");
            if (table.length) {
                table.find(".custom-message-cc-only").toggle(t === "cc");
                table.find(".custom-message-pc-only").toggle(t === "pc");
            }
            that.#customMessageRawRows.forEach((row) => row.toggle(t === "raw"));
        }
        typeSelect.on("change", updateVisibility);
        // Run after append: schedule so DOM is ready
        setTimeout(updateVisibility, 0);

        const row = (label, input, extraClass = "") =>
            $('<tr class="custom-message-simple ' + extraClass + '" />').append(
                $('<td />').append($('<span />').text(label)),
                $('<td />').append(input)
            );

        return [
            $('<tr class="custom-message-simple" />').append(
                $('<td colspan="2" />').append($('<strong />').text("Simple edit (CC / PC)"))
            ),
            row("Type", typeSelect),
            row("Channel (1–16)", channelInput),
            row("CC# (0–127)", ccInput, "custom-message-cc-only"),
            row("Value (on)", valueOnInput, "custom-message-cc-only"),
            row("Value (off)", valueOffInput, "custom-message-cc-only"),
            row("Program (0–127)", pcInput, "custom-message-pc-only"),
            row("Label", labelInput),
            row("Color", colorSelect),
            row("Toggle (on/off)", toggleCheck),
            row("Group (radio)", groupInput)
        ];
    }

    /**
     * Returns an action definition which can be added to the Configuration.
     */
    createActionDefinition() {
        const that = this;

        function getName() {
            if (that.actionDefinition.name == "PagerAction.proxy") {
                const pagerProxy = that.pagerProxy();
                
                if (pagerProxy) {
                    return that.actionDefinition.name.replace("PagerAction", pagerProxy)
                }
            }
            return that.actionDefinition.name;
        }

        if (this.actionDefinition.name === "CUSTOM_MESSAGE" && this.inputs.has("_midiType")) {
            const type = this.inputs.get("_midiType").val();
            const ch = parseInt(this.inputs.get("_channel").val(), 10) || 1;
            const args = [];
            const simple = {
                message: null,
                message_release: null,
                text: null,
                color: null,
                toggle: null,
                group: null
            };
            if (type === "cc" || type === "pc") {
                const built = buildCustomMessage(type, {
                    channel: ch,
                    cc: parseInt(this.inputs.get("_cc").val(), 10),
                    valueOn: parseInt(this.inputs.get("_valueOn").val(), 10),
                    valueOff: parseInt(this.inputs.get("_valueOff").val(), 10),
                    pc: parseInt(this.inputs.get("_pc").val(), 10)
                });
                simple.message = built.message;
                simple.message_release = built.message_release;
            }
            simple.text = Tools.autoQuote(this.inputs.get("_simpleLabel").val() || "");
            simple.color = this.inputs.get("_simpleColor").val() || "Colors.WHITE";
            simple.toggle = this.inputs.get("_simpleToggle").prop("checked") ? "True" : "False";
            const groupStr = (this.inputs.get("_simpleGroup").val() || "").trim();
            simple.group = groupStr ? Tools.autoQuote(groupStr) : "None";

            for (const param of this.actionDefinition.parameters) {
                let value;
                if (param.name === "message") value = simple.message != null ? simple.message : this.#getInputValue(this.inputs.get(param.name), param);
                else if (param.name === "message_release") value = simple.message_release != null ? simple.message_release : this.#getInputValue(this.inputs.get(param.name), param);
                else if (param.name === "text") value = simple.text;
                else if (param.name === "color") value = simple.color;
                else if (param.name === "toggle") value = simple.toggle;
                else if (param.name === "group") value = simple.group;
                else {
                    const input = this.inputs.get(param.name);
                    if (!input) continue;
                    value = this.#getInputValue(input, param);
                }
                const def = param.default;
                if (!param.hasOwnProperty("default") || value != def) {
                    args.push({ name: param.name, value: value });
                }
            }
            return {
                name: getName(),
                assign: this.inputs.get("assign").val(),
                arguments: args
            };
        }

        return {
            name: getName(),
            assign: this.inputs.get('assign').val(),
            arguments: this.actionDefinition.parameters
                .filter((param) => {
                    const input = that.inputs.get(param.name);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    const value = that.#getInputValue(input, param);

                    return !param.hasOwnProperty("default") || (value != param.default);
                })
                .map((param) => {
                    const input = that.inputs.get(param.name);
                    if (!input) throw new Error("No input for param " + param.name + " found");
        
                    return {
                        name: param.name,
                        value: that.#getInputValue(input, param)
                    };
                })
        }
    }

    /**
     * Returns if the user selected hold or not (JS bool, no python value)
     */
    hold() {
        if (this.actionDefinition.meta.data.target == "AdafruitSwitch") {
            return !!this.inputs.get("hold").prop('checked');
        }
        return false;
    }

    /**
     * Sets the hold input
     */
    async setHold(hold) {
        if (this.actionDefinition.meta.data.target != "AdafruitSwitch") {
            return;
        }
        this.inputs.get("hold").prop('checked', !!hold)
        // await this.update();
    }

    /**
     * Returns the assign value if set
     */
    assign() {
        if (!this.inputs.has("assign")) return null;
        return this.inputs.get("assign").val();
    }

    /**
     * Sets the assign input
     */
    async setAssign(assign) {
        this.inputs.get("assign").val(assign);
        // await this.update();     
    }

    /**
     * Returns the pager proxy value if set
     */
    pagerProxy() {
        if (!this.inputs.has("pager")) return null;
        return this.inputs.get("pager").val();
    }

    /**
     * Sets the pager proxy input
     */
    async setPagerProxy(proxy) {
        this.inputs.get("pager").val(proxy);   
        // await this.update();
    }

    /**
     * Sets the input values to the passed arguments list's values
     */
    async setArguments(args) {
        await this.update();

        for (const arg of args) {
            await this.setArgument(arg.name, arg.value);
            const param = this.getParameterDefinition(arg.name);
            if (param && param.meta.getDefaultValue() != arg.value) {
                this.showParameter(arg.name);
            }
        }

        if (this.actionDefinition.name === "CUSTOM_MESSAGE" && this.inputs.has("_midiType")) {
            const msgArg = args.find((a) => a.name === "message");
            if (msgArg) {
                const parsed = parseCustomMessage(msgArg.value);
                this.inputs.get("_midiType").val(parsed.type === "raw" ? "raw" : parsed.type);
                this.inputs.get("_channel").val(parsed.channel || 1);
                this.inputs.get("_cc").val(parsed.cc ?? 0);
                this.inputs.get("_valueOn").val(parsed.valueOn ?? 127);
                this.inputs.get("_pc").val(parsed.pc ?? 0);
                const relArg = args.find((a) => a.name === "message_release");
                if (relArg && relArg.value && relArg.value !== "None") {
                    const offParsed = parseCustomMessage(relArg.value);
                    if (offParsed.type === "cc" && offParsed.valueOn !== undefined) {
                        this.inputs.get("_valueOff").val(offParsed.valueOn);
                    }
                }
                const textArg = args.find((a) => a.name === "text");
                if (textArg != null) {
                    const v = textArg.value;
                    this.inputs.get("_simpleLabel").val(typeof v === "string" ? v.replace(/^["']|["']$/g, "") : v);
                }
                const colorArg = args.find((a) => a.name === "color");
                if (colorArg != null) this.inputs.get("_simpleColor").val(colorArg.value);
                const toggleArg = args.find((a) => a.name === "toggle");
                if (toggleArg != null) this.inputs.get("_simpleToggle").prop("checked", toggleArg.value === "True");
                const groupArg = args.find((a) => a.name === "group");
                if (groupArg != null && groupArg.value !== "None") {
                    this.inputs.get("_simpleGroup").val(groupArg.value.replace(/^["']|["']$/g, ""));
                }
                this.inputs.get("_midiType").trigger("change");
            }
        }

        await this.update();
    }

    /**
     * Set the value of a parameter input
     */
    async setArgument(name, value) {
        await this.update();

        // Get parameter definition first
        const param = this.getParameterDefinition(name);
        if (!param) throw new Error("Parameter " + name + " not found");

        const input = this.inputs.get(param.name);
        if (!input) throw new Error("No input for param " + param.name + " found");

        await this.#setInputValue(input, param, value);

        await this.update();
    }

    /**
     * Shows an advanced parameter
     */
    showParameter(name) {
        for (const level of this.#advancedRows) {
            for (const row of level) {
                if (row.parameterName == name) {
                    row.row.show();
                }
            }
        }
    }

    /**
     * Searches a parameter mode by name
     */
    getParameterDefinition(name) {
        for (const param of this.actionDefinition.parameters) {
            if (param.name == name) return param;
        }
        return null;
    }

    /**
     * Determine the comment for the action
     */
    #getActionComment() {
        if (!this.actionDefinition.comment) return "No information available";
        let comment = "" + this.actionDefinition.comment;

        //if (comment.slice(-1) != ".") comment += ".";

        return comment;
    }

    /**
     * Determine parameter comment
     */
    #getParameterComment(param) {
        if (param.meta.data.comment) return param.meta.data.comment;
        if (!param.comment) return "";
        return param.comment;
    }

    /**
     * Update the UI
     */
    async update() {
        await this.#pagers.update();
    }

    /**
     * Generates the DOM for one parameter
     */
    async #createInput(param) {
        const type = param.meta.type();

        const that = this;
        async function onChange() {            
            await that.update();
        }

        switch(type) {
            case "bool": {                             
                return $('<input type="checkbox" />')
                .prop('checked', param.meta.getDefaultValue() == "True")
                .on('change', onChange)
            }

            case "int": {
                return (await this.#getNumberInput(param))
                .on('change', onChange)
                .val(param.meta.getDefaultValue());
            }

            case 'select': {
                const values = await param.meta.getValues();
                if (values) {
                    return $('<select />').append(
                        values.map((option) => 
                            $('<option value="' + option.value + '" />')
                            .text(option.name)
                        )
                    )
                    .on('change', onChange)
                    .val(param.meta.getDefaultValue())
                }
                break;
            }

            case 'select-page': {
                return $('<select />')
                .on('change', onChange)
            }
                
            case 'pages': {
                // Dedicated type for the pager actions's "pages" parameter
                return this.#pagers.getPagesList(onChange);
            }
        }        

        return $('<input type="text" />')
            .on('change', onChange)
            .val(param.meta.getDefaultValue())
    }

    /**
     * If the parameter is of type "color", this returns additional elements to add to the input. Also
     * other special types with additional inputs are created here. 
     * 
     * If not special, an empty array is returned.
     */
    async #createAdditionalInputOptions(input, param) {
        switch (param.meta.type()) {
            case "color": return this.#createAdditionalColorInputOptions(input, param);
            case "select-free": return this.#createAdditionalSelectFreeInputOptions(input, param);
        }
        
        return [];
    }

    async #createAdditionalSelectFreeInputOptions(input, param) {
        const that = this;
        return [
            $('<select class="parameter-option" />').append(
                (await param.meta.getValues())
                .concat([{
                    name: "Select..."
                }])
                .map((item) => 
                    $('<option value="' + item.name + '" />')
                    .text(item.name)
                )
            )
            .on('change', async function() {
                const value = $(this).val();
                if (value == "Select...") return;

                await that.setArgument(param.name, value);

                $(this).val("Select...")
            })
            .val("Select..."),
        ];
    }

    async #createAdditionalColorInputOptions(input, param) {
        let colorInput = null;
        const that = this;

        async function updateColorInput() {
            const color = await that.parserFrontend.parser.resolveColor(input.val());
            if (color) {
                colorInput.val(Tools.rgbToHex(color))
            }
        }

        const ret = [
            $('<select class="parameter-option" />').append(
                (await this.parserFrontend.parser.getAvailableColors())
                .concat([{
                    name: "Select color..."
                }])
                .map((item) => 
                    $('<option value="' + item.name + '" />')
                    .text(item.name)
                )
            )
            .on('change', async function() {
                const color = $(this).val();
                if (color == "Select color...") return;

                await that.setArgument(param.name, color);

                $(this).val("Select color...")

                await updateColorInput();
            })
            .val("Select color..."),

            colorInput = $('<input type="color" class="parameter-option parameter-link" />')
            .on('change', async function() {
                const rgb = Tools.hexToRgb($(this).val());

                await that.setArgument(param.name, "(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ")");
            })
        ];

        input.on('change', updateColorInput)
        await updateColorInput();

        return ret;
    }

    /**
     * Returns a parameter value by name
     */
    getParameterValue(name) {
        const param = this.getParameterDefinition(name);
        if (!param) return null;

        const input = this.inputs.get(param.name);
        if (!input) return null;

        return this.#getInputValue(input, param);        
    }

    /**
     * Converts the input values to action argument values
     */
    #getInputValue(input, param) {
        const type = param.meta.type();

        switch(type) {
            case "bool": return input.prop('checked') ? "True" : "False";
            case "pages": return this.#pagers.pages.get();
        }        

        let value = input.val();
        if (value == "") value = param.meta.getDefaultValue();

        return param.meta.convertInput(value);
    }

    /**
     * Sets the input value according to an argumen/parameter value
     */
    async #setInputValue(input, param, value) {
        const type = param.meta.type();

        switch(type) {
            case "bool": 
                input.prop('checked', value == "True");
                input.trigger('change');
                break;

            case "pages":
                await this.#pagers.pages.set(value)
                break;

            default:
                input.val(value.replaceAll('"', "'"));
                input.trigger('change');
        }      
    }

    /**
     * Create a numeric input (int)
     */
    async #getNumberInput(param) {
        const values = await param.meta.getValues();
        if (!values) {
            return $('<input type="number" />');
        }

        return $('<select />').append(
            values.map((option) => 
                $('<option value="' + option.value + '" />')
                .text(option.name)
            )
        ) 
    }
}