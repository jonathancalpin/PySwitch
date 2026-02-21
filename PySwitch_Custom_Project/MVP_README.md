# MIDI Captain Mini 6 – MVP (Fresh Start)

This project has been reset and rebuilt from the **standard PySwitch firmware and emulator** based on MVP specifications.

## What Changed

1. **Content (device firmware)** – `content/` in project root  
   - Generic MIDI (no Kemper protocol)  
   - 4 pages: Logic, ToneX, GP-5, Looper  
   - Page change: **Hold Button B**  
   - CUSTOM_MESSAGE for CC toggles, PC selects  
   - 3×2 display, color per switch, toggle dim/bright  

2. **Web emulator** – `web/` in project root  
   - Standard PySwitch web emulator  
   - Templates updated with MVP config  
   - Use `#template/MIDICaptain Mini 6` to load  

3. **Custom configs removed**  
   - `combo-navigation` template removed  
   - Combo paging (A+B/B+C) removed for now  

4. **Deploy** – `deploy-to-device.sh` in project root  
   - Copies from `content/` to device volume  

## Run Emulator

```bash
cd web
docker compose up
# Open http://localhost
# Go to #template/MIDICaptain%20Mini%206 or select MIDICaptain Mini 6 template
```

## Deploy to Device

```bash
# Put device in USB storage mode first
./deploy-to-device.sh
# Eject volume and restart device
```

## MVP Spec

- **Device:** PaintAudio MIDI Captain Mini 6  
- **Display:** 6 blocks (3×2), 240×240, color per switch  
- **Pages:** Logic (ch1), ToneX (ch2), GP-5 (ch3), Looper (ch4)  
- **Page change:** Hold Button B  
- **Toggle:** Bright when on, dim when off  
