# Ampz state sync (MIDI Captain Mini 6)

The stomp switches follow the effect state in Ampz, so the LEDs stay correct when presets change, when an effect is toggled on screen, and after reconnecting. The firmware side is done. Ampz has to send the state (see "What Ampz sends" below).

## How it works

- Each stomp switch sends its CC with **127 when turned on, 0 when turned off**, on MIDI channel 1.
- Each stomp switch also **listens for that same CC** coming back. A value of **64 or more lights it, below 64 turns it off**.
- Every incoming message is applied, even if it repeats the last value, so a preset that sends "off" twice in a row still turns the LED off after a local press.
- The state is kept when you change pages. A stomp on a hidden page still updates, and shows the right state when you page back to it.
- The incoming MIDI channel is not checked. Ampz ignores channels too.
- Receiving never sends anything, and there is no MIDI thru, so an echo from Ampz can't loop.
- Switches that only fire (Tap, looper, scenes, TUNER and CLEAR holds) don't listen.

Code: `listen = True` on `CUSTOM_MESSAGE` (toggle mode with a CC message) in `content/lib/pyswitch/clients/local/actions/custom.py`. Tests: `test/pyswitch/test_local_action_custom_message.py` (`TestLocalCustomMessageListen`).

## Connections

Both connections work at the same time. Normally only one is plugged in.

- **USB**: in and out, as before.
- **MIDI in/out jacks**: in and out (`content/communication.py`). Use these for a Bluetooth MIDI adapter such as a CME WIDI Jack. Set the adapter's TRS type to match the Captain's jacks for both directions. If only one direction works, the TRS type is the usual cause.

Switch presses go out of both ports. If a user has both connected to Ampz at once, Ampz de-duplicates (one active port per controller).

## CC table

All on MIDI channel 1. "Stomp" rows listen for state. Learn stomps in Ampz as **Stomp Mappings in Latch mode**, and everything else as Action Mappings.

| Page | Switch | Label | CC | Type |
|---|---|---|---|---|
| Stomp A | 1 | DIST | 83 | Stomp |
| Stomp A | 2 | DELAY | 82 | Stomp |
| Stomp A | 3 | BOOST (EQ) | 90 | Stomp |
| Stomp A | A | CHORUS | 84 | Stomp (hold: TUNER 68) |
| Stomp A | B | TREM | 89 | Stomp |
| Stomp A | C | PHASER | 87 | Stomp |
| Stomp B | 1 | PITCH | 80 | Stomp |
| Stomp B | 2 | WAH | 81 | Stomp |
| Stomp B | 3 | Tap | 85 | Action |
| Stomp B | A | FLANGER | 91 | Stomp (hold: TUNER 68) |
| Stomp B | B | COMP | 86 | Stomp |
| Stomp B | C | REVERB | 88 | Stomp |
| Looper | 1 | REC | 60 | Action |
| Looper | 2 | PLAY | 61 | Action |
| Looper | 3 | STOP | 62 | Action |
| Looper | A | UNDO | 63 | Action (hold: CLEAR 100) |
| Looper | B | SCN- | 104 | Action |
| Looper | C | SCN+ | 105 | Action |

Paging: A+B = previous page, B+C = next page (wraps). Switches 1–3 send instantly; A–C wait 150 ms for the combo.

## What Ampz sends

For every stomp mapping, the learned CC with 127 (on) or 0 (off):

1. **After a preset loads**, from any source: every stomp's state. A family that isn't in the preset sends 0.
2. **When an effect is toggled on screen**: that stomp's state.
3. **When the controller's port appears** (connect, reconnect, Bluetooth pairing): every stomp's state, because the Captain starts with all LEDs off.
4. **After handling a press from the Captain**: the resulting state. This firmware doesn't need the echo, but it's harmless, and other controllers do need it.

## Editing the layout

The web configurator may not know the `listen` option. If you re-save `inputs.py` from it, check that `listen = True` is still on each stomp switch.

## Deploy and test

1. Plug in the pedal holding switch 1 so it mounts as `MIDICAPTAIN`, then run `./deploy-to-device.sh`.
2. Eject, then power-cycle without holding switch 1.
3. Test, with Ampz connected over USB:
   - Press a stomp: the effect toggles in Ampz and the LED follows.
   - Toggle the effect on screen in Ampz: the LED follows (needs the Ampz side).
   - Change presets: all stomp LEDs match the new preset (needs the Ampz side).
   - Page away and back: the LEDs still match.
4. Repeat over the MIDI jacks with the Bluetooth adapter.
