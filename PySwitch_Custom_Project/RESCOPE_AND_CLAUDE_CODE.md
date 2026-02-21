# Rescoping the Project with Claude Code (Terminal)

Use this so **Claude Code** (or another AI in the terminal) and **Cursor** share the same project scope, tasks, and context. That keeps programming consistent.

---

## 1. What to use Claude Code for

- **Rescope** the project: align tasks, scope, and todos with the target behavior (3×2 display, toggle dim/bright, preset active, editor for CC/PC/notes/toggle/colors, combo A+B/B+C in editor).
- **Update** project docs so they match: ACTION_PLAN.md, PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md, CURSOR_INITIAL_PROMPT.md, and any task/scope lists.
- **Keep context consistent** so the next session (Cursor or Claude Code) continues from the right place.

---

## 2. How to run Claude Code in the terminal

If you have **Claude Code** (or a similar CLI) installed:

1. Open a terminal in the project root (e.g. `PySwitch_Custom_Project` or repo root).
2. Run your usual command, for example:
   - `claude` or `claudecode` (depends on your install).
   - Or: `npx @anthropic-ai/claude-code` / your project’s script.
3. At the start of the session, **paste or attach**:
   - This file: `RESCOPE_AND_CLAUDE_CODE.md`
   - `ACTION_PLAN.md`
   - `PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md`
   - `CURSOR_INITIAL_PROMPT.md`
4. Say something like:

   > I'm rescoping the MIDI Captain Mini 6 PySwitch project. Use ACTION_PLAN.md and PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md as the source of truth. Please:
   > 1. Update the project tasks/scope/todos so they match the target: even 3×2 display, color per switch, toggle dim/bright, preset active, editor for CC/PC/notes/toggle/colors, and A+B/B+C page up/down in the editor.
   > 2. Update ACTION_PLAN, PROJECT_SCOPE, and CURSOR_INITIAL_PROMPT so they're consistent and any AI (Cursor or Claude Code) can continue from here.

If you don’t have Claude Code, you can do the same rescoping in **Cursor** chat: attach ACTION_PLAN.md, PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md, CURSOR_INITIAL_PROMPT.md, and this file, then ask to rescope and keep all docs consistent.

---

## 3. What “rescoped” should include

- **Device (deploy_stock):** 3×2 display, names and colors per page, toggle dim/bright, preset active, hold B = page. No over‑engineering (e.g. no input rebuild on page change that breaks toggles).
- **Editor:** Support for A+B and B+C as page up/down; easy adjustment of CC, PC, notes, toggle, and colors.
- **Docs:** Single coherent story across ACTION_PLAN, PROJECT_SCOPE, and CURSOR_INITIAL_PROMPT; task list and “current phase” updated so the next session knows what’s done and what’s next.

---

## 4. After rescoping

- **Commit** the updated ACTION_PLAN.md, PROJECT_SCOPE_MIDI_CAPTAIN_MINI_6.md, CURSOR_INITIAL_PROMPT.md (and any new task/scope files).
- **In Cursor:** Start with “Continue from ACTION_PLAN” or “What’s the next task?” so the AI uses the new scope.
- **Deploy device:** Run `./deploy-to-device.sh` when the volume is mounted to load the stable `deploy_stock` firmware.
