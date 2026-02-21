# Custom PySwitch Web Editor

This is a forked version of the PySwitch web editor with added support for **combo-based page navigation** (A+B = Next Page, B+C = Previous Page).

## Features

- **Combo Page Navigation**: Configure A+B and B+C button combos for page navigation
- **Multi-Page Support**: Create and manage multiple pages with different MIDI configurations
- **Visual Editor**: Edit CC/PC values, colors, and labels through a graphical interface
- **Display Editor**: Edit each of the 6 display squares – **text name** (Initial Text) and **color** (Text Color, Back Color) – and see a graphical preview of each page in the emulator (no need for real-time device sync)
- **Device Integration**: Save directly to your MIDI Captain via MidiBridge

## Quick Start

### 1. Run the Web Editor

```bash
cd web-editor
docker compose up -d
```

Then open **http://localhost:8080** in Chrome.

**Important:** Use the **served** app at http://localhost:8080 (from `npm run serve` or Docker in this `web-editor` folder) to get the full UI: live panel, **Page ↑ / Page ↓** (bank up/down), **A+B** and **B+C** combo test buttons. Opening the HTML via `file://` or from a different server may load a different build and won’t show those enhancements. **“No connection”** on 8080 is normal when no physical MIDI device is connected; the emulator and editor work without a device.

### 2. Connect Your Device (optional)

1. Plug in your MIDI Captain (running custom PySwitch firmware)
2. Click "Connect Device" in the web editor
3. Select your MIDI Captain from the MIDI ports

### 3. Edit Configuration

- Click the **layer icon** (📑) to open the Combo Page Navigation editor
- Add/remove pages
- Configure button actions for each page
- Set colors and MIDI channels

### 4. Save to Device

Press Ctrl+S or click Save to write the configuration to your device.

### 5. Testing the emulator (Playwright)

To confirm the emulator loads and syncs correctly (e.g. connection button not stuck on hourglass):

1. Install Node.js and npm if needed, then from `web-editor`: `npm install`
2. In one terminal: `npm run serve` (or `docker compose up -d`)
3. In another: `npm run test:emulator`

See `tests/README.md` for details and custom URLs.

## Combo Page Navigation

The custom firmware uses button combinations for page navigation:

| Combo | Action |
|-------|--------|
| A + B | Next Page |
| B + C | Previous Page |

This eliminates the need for long-press page switching, avoiding accidental triggers.

## Configuration Structure

The `inputs.py` file uses this structure:

```python
# Page definitions
PAGE_1 = {
    "name": "Logic",
    "channel": 1,
    "midi_out": "USB",
    "color_theme": Colors.BLUE,
    "switches": [...]
}

# Pages array (order matters)
Pages = [PAGE_1, PAGE_2, PAGE_3, PAGE_4]

# Combo configuration
ComboConfig = {
    "enabled": True,
    "combo_switches": ['A', 'B', 'C'],
    "combo_window_ms": 50,
}

# Required for PySwitch
Inputs = PAGE_1["switches"]
```

## Requirements

- Docker (for running the web editor locally)
- Chrome browser (recommended for Web MIDI support)
- MIDI Captain with custom PySwitch firmware installed

## File Structure

```
web-editor/
├── compose.yaml          # Docker configuration
├── Dockerfile            # Docker image definition
├── htdocs/               # Web application files
│   ├── js/               # JavaScript source
│   │   └── ui/parser/
│   │       └── ComboPageProperties.js  # Combo UI component
│   ├── python/parser/    # Python parsers
│   │   ├── ComboConfigExtractor.py     # Combo config parser
│   │   └── ComboCodeGenerator.py       # Code generator
│   ├── styles/
│   │   └── combo-pages.css             # Combo UI styles
│   └── templates/
│       └── combo-navigation/           # Template configuration
└── README.md
```

## Development

To modify the web editor:

1. Edit files in `htdocs/`
2. Refresh the browser (no rebuild needed for JS/CSS changes)
3. For Python changes, restart the Docker container

## Troubleshooting

### Web editor won't connect to device

1. Make sure you're using Chrome (Safari doesn't support Web MIDI)
2. Allow MIDI access when prompted
3. Ensure the device is running custom PySwitch firmware

### Changes not saving

1. Check that MidiBridge is enabled in config.py
2. Verify the device is connected (check connection indicator)
3. Try disconnecting and reconnecting

### Combo detection not working

1. Verify `ComboConfig` is present in inputs.py
2. Check that `combo_window_ms` is set appropriately (50-100ms recommended)
3. Ensure custom controller modules are installed on the device
