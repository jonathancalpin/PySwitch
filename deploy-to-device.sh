#!/bin/bash
#
# Deploy standard PySwitch MVP firmware to MIDI Captain Mini 6.
# Source: content/ (standard firmware)
# Page change: A+B = page down, B+C = page up (combo)
#
# Usage:
#   1. Put device in USB storage mode (hold button during plug-in).
#   2. Wait until volume appears (e.g. /Volumes/MIDICAPTAIN).
#   3. Run: ./deploy-to-device.sh [volume_path]
#   4. Eject volume and restart device.
#

set -e

VOLUME="${1:-/Volumes/MIDICAPTAIN}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${SCRIPT_DIR}/content"

if [ ! -d "$SOURCE" ]; then
  echo "Error: content not found at $SOURCE"
  exit 1
fi

if [ ! -d "$VOLUME" ]; then
  echo "Error: Volume not found at $VOLUME"
  echo "Usage: $0 [volume_path]"
  exit 1
fi

echo "Deploying MVP firmware from $SOURCE to $VOLUME"
echo ""

cp "$SOURCE/code.py" "$VOLUME/"
cp "$SOURCE/boot.py" "$VOLUME/"
cp "$SOURCE/config.py" "$VOLUME/"
cp "$SOURCE/inputs.py" "$VOLUME/"
cp "$SOURCE/display.py" "$VOLUME/"
cp "$SOURCE/communication.py" "$VOLUME/"
echo "  code.py, boot.py, config.py, inputs.py, display.py, communication.py"

cp -r "$SOURCE/lib" "$VOLUME/"
echo "  lib/"

cp -r "$SOURCE/fonts" "$VOLUME/"
echo "  fonts/"

echo ""
echo "Done. Eject $VOLUME and restart the device."
echo "Page nav: A+B = page down, B+C = page up (press within 50ms)."
