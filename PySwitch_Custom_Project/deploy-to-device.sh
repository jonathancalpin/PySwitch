#!/bin/bash
#
# Deploy combo firmware to MIDI Captain Mini 6 (deploy_stock).
# - 3x2 display, color per switch, toggle dim/bright, preset active.
# - Page change: A+B = Page Down, B+C = Page Up (combo, press within 50ms).
# - Uses PagerAction (no input rebuild) - stable, no flash/freeze.
#
# Usage:
#   1. Put the device in USB storage mode (e.g. hold button during plug-in).
#   2. Wait until the volume appears (e.g. /Volumes/MIDICAPTAIN).
#   3. Run: ./deploy-to-device.sh [volume_path]
#   4. Eject the volume and restart the device.
#

set -e

VOLUME="${1:-/Volumes/MIDICAPTAIN}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
SOURCE="${PROJECT_DIR}/deploy_stock"

if [ ! -d "$SOURCE" ]; then
  echo "Error: deploy_stock not found at $SOURCE"
  exit 1
fi

if [ ! -d "$VOLUME" ]; then
  echo "Error: Volume not found at $VOLUME"
  echo "Usage: $0 [volume_path]"
  exit 1
fi

echo "Deploying combo firmware (A+B = Page Down, B+C = Page Up) from $SOURCE to $VOLUME"
echo ""

cp "$SOURCE/code.py" "$VOLUME/"
cp "$SOURCE/config.py" "$VOLUME/"
cp "$SOURCE/inputs.py" "$VOLUME/"
cp "$SOURCE/display.py" "$VOLUME/"
cp "$SOURCE/communication.py" "$VOLUME/"
echo "  code.py, config.py, inputs.py, display.py, communication.py"

cp "$SOURCE/lib/pyswitch/process.py" "$VOLUME/lib/pyswitch/"
cp "$SOURCE/lib/pyswitch/controller/controller.py" "$VOLUME/lib/pyswitch/controller/"
cp "$SOURCE/lib/pyswitch/controller/controller_combo.py" "$VOLUME/lib/pyswitch/controller/"
cp "$SOURCE/lib/pyswitch/clients/local/actions/pager.py" "$VOLUME/lib/pyswitch/clients/local/actions/"
cp "$SOURCE/lib/pyswitch/clients/local/actions/custom.py" "$VOLUME/lib/pyswitch/clients/local/actions/"
echo "  lib/pyswitch/ (process, controller, controller_combo, pager, custom)"

if [ -f "$SOURCE/fonts/PT40.pcf" ]; then
  mkdir -p "$VOLUME/fonts"
  cp "$SOURCE/fonts/PT40.pcf" "$VOLUME/fonts/PT40.pcf"
  echo "  fonts/PT40.pcf"
fi

echo ""
echo "Done. Eject $VOLUME and restart the device."
echo "Page nav: A+B = Page Down, B+C = Page Up (press second button within 50ms)."
