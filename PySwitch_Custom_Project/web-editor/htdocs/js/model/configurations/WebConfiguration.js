/**
 * Configuration loaded from the web
 */
class WebConfiguration extends Configuration {

    #path = null;
    
    constructor(controller, path, title = null) {
        if (!title) {
            const splt = decodeURI(path).split("/");
            title = splt.pop();
        }

        super(controller, title);
        this.#path = path;

    }

    /**
     * Loads config files from the web.
     */
    async load() {
        const bust = "?_v=" + PySwitchRunner.CACHE_VERSION;
        return {
            inputs_py: await Tools.fetch(this.#path + "/inputs.py" + bust),
            display_py: await Tools.fetch(this.#path + "/display.py" + bust)
        }
    }
}