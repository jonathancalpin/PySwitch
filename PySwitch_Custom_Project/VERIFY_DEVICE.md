# Device verification checklist (first task)

Use this when confirming the device after deploy. Tick each item as you verify it.

---

## Before testing

- [ ] Device is powered and connected (USB storage ejected, device rebooted after last deploy).
- [ ] If unsure, redeploy: mount device (e.g. hold button), run `./deploy-to-device.sh`, eject, reboot.

---

## 1. Display (3×2)

- [ ] Screen shows **6 blocks** in a grid (2 rows × 3 columns).
- [ ] Top row = buttons 1, 2, 3; bottom row = buttons A, B, C.
- [ ] Each block shows **text** (effect name, e.g. Comp, EQ, Delay on page 1).
- [ ] Each block has a **background color** (not all the same; matches switch color).

---

## 2. Toggle (dim / bright)

- [ ] On **page 1 (Logic)**: press a **toggle** button (e.g. Comp, EQ, Delay). Block gets **brighter** when on.
- [ ] Press again to turn off. Block gets **dimmer** when off (still same color, just dimmer).
- [ ] Text stays the same on/off.

---

## 3. Preset / PC (stays active)

- [ ] Change to a page with **preset/PC** buttons (e.g. page 2 ToneX: Clean, Crunch, Lead).
- [ ] Press one preset (e.g. Clean). Its block stays **bright** (active).
- [ ] Press another preset (e.g. Crunch). That one becomes bright, first stays as configured (e.g. dim or bright depending on design).

---

## 4. Page change (hold B)

- [ ] **HOLD** button **B** (bottom center) for the hold duration (e.g. ~600 ms).
- [ ] Page changes: display and switch actions change to next page (e.g. Logic → ToneX → GP-5 → Looper).
- [ ] Hold B again to cycle to next page. All 4 pages reachable.
- [ ] Display and LED colors/names match the **current page**.

---

## 5. No bad behavior

- [ ] No blank display on boot (or only briefly).
- [ ] No stuck/frozen display when changing pages.
- [ ] Toggle buttons don’t “stick” (press = on, press again = off).
- [ ] Single tap on A, B, C does **not** change page (only hold B does).

---

## After verification

- If **all checked:** tick **“Confirm on hardware”** in TODOS.md and update ACTION_PLAN.md (last completed = confirm device).
- If **something fails:** note which item (e.g. “toggle not dimming”) and we can fix in deploy_stock or config.
