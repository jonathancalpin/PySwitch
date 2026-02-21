#!/bin/bash
#
# Build a portable, self-contained PySwitch emulator that runs without Docker.
# Copies the web editor, firmware library, and examples into a single directory,
# then generates static toc.json files so no PHP server is needed.
#
# Usage:
#   ./build-portable-emulator.sh [output-path]
#
# Default output: ./portable-emulator/
#
# To run the emulator:
#   cd <output-path> && python3 -m http.server 8000
#   Then open http://localhost:8000 in your browser.
#
# On macOS you can also double-click start-emulator.command in the output folder.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="${1:-${SCRIPT_DIR}/portable-emulator}"
HTDOCS="${SCRIPT_DIR}/PySwitch_Custom_Project/web-editor/htdocs"

if [ ! -d "$HTDOCS" ]; then
  echo "Error: web-editor htdocs not found at $HTDOCS"
  exit 1
fi

if [ ! -d "${SCRIPT_DIR}/content" ]; then
  echo "Error: content/ not found at ${SCRIPT_DIR}/content"
  exit 1
fi

echo "Building portable emulator → $OUTPUT"
echo ""

# Clean previous build
rm -rf "$OUTPUT"
mkdir -p "$OUTPUT"

# Copy htdocs (resolve symlinks so everything is self-contained)
echo "  Copying web editor (resolving symlinks)..."
cp -rL "$HTDOCS/" "$OUTPUT/"

# Ensure content and examples are present (cp -rL above resolves the symlinks,
# but if they were broken or missing, copy explicitly)
if [ ! -d "$OUTPUT/circuitpy" ]; then
  echo "  Copying content/ → circuitpy/"
  cp -r "${SCRIPT_DIR}/content" "$OUTPUT/circuitpy"
fi

if [ ! -d "$OUTPUT/examples" ]; then
  echo "  Copying examples/ → examples/"
  cp -r "${SCRIPT_DIR}/examples" "$OUTPUT/examples"
fi

# Generate static toc.json files
echo "  Generating toc.json files..."

# Directories that need a toc.json for the emulator's file browser
TOC_DIRS=(
  "templates"
  "examples"
  "circuitpy/lib/pyswitch/clients"
  "circuitpy/fonts"
  "custom-deploy/lib/pyswitch/clients"
  "custom-deploy/fonts"
)

# Exclusions matching the PHP toc.php behavior (skip meta-files)
EXCLUDES="toc.php toc.json .DS_Store __pycache__"

python3 - "$OUTPUT" "$EXCLUDES" "${TOC_DIRS[@]}" << 'PYTHON_EOF'
import sys, os, json

output_root = sys.argv[1]
excludes = set(sys.argv[2].split())
toc_dirs = sys.argv[3:]

def build_toc(path):
    """Recursively build a TOC structure matching the PHP toc.php format."""
    children = []
    try:
        entries = sorted(os.listdir(path))
    except FileNotFoundError:
        return children

    for name in entries:
        if name in excludes or name.startswith('.'):
            continue
        full = os.path.join(path, name)
        if os.path.isdir(full):
            children.append({
                "type": "dir",
                "name": name,
                "children": build_toc(full)
            })
        elif os.path.isfile(full):
            children.append({
                "type": "file",
                "name": name
            })
    return children

for rel_dir in toc_dirs:
    abs_dir = os.path.join(output_root, rel_dir)
    if not os.path.isdir(abs_dir):
        print(f"    Warning: {rel_dir}/ not found, skipping toc.json")
        continue

    toc = {
        "type": "dir",
        "name": "",
        "path": "",
        "children": build_toc(abs_dir)
    }

    toc_path = os.path.join(abs_dir, "toc.json")
    with open(toc_path, "w") as f:
        json.dump(toc, f, indent=4)
    print(f"    {rel_dir}/toc.json")

PYTHON_EOF

# Create macOS double-click launcher
cat > "$OUTPUT/start-emulator.command" << 'LAUNCHER_EOF'
#!/bin/bash
cd "$(dirname "$0")"
PORT=8000
echo "Starting PySwitch Emulator on http://localhost:$PORT"
echo "Press Ctrl-C to stop."
echo ""
open "http://localhost:$PORT"
python3 -m http.server $PORT
LAUNCHER_EOF
chmod +x "$OUTPUT/start-emulator.command"

echo ""
echo "Done! Portable emulator built at: $OUTPUT"
echo ""
echo "To run:"
echo "  macOS:  Double-click $OUTPUT/start-emulator.command"
echo "  Any OS: cd $OUTPUT && python3 -m http.server 8000"
echo "  Then open http://localhost:8000"
