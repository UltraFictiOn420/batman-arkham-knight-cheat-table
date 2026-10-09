# Status and testing — 2026-10-09

First original test build: v1. User gameplay confirmation pending for ALL features. Live mapping identified Batman at 100/100 HP, the player/controller/world chain, 174 eligible loaded enemies, and 9 player inventory gadgets in the observed session. Reflected core and range offsets were checked.

Actual Lua executed against live process reads with all writes redirected to an in-memory overlay. Verified initialization without gameplay writes, health refill/off/no resurrection, enemy cap/off/one-hit, range edits/restoration, save/teleport/undo/upward moves and process-retarget guard. XML, all embedded Lua syntax, and record IDs checked. This is not proof of in-game behavior.

No live writes were made by the discovery/test scripts. `test_knight_runtime.py` requires a currently running matching game and module base; its mocks intercept every write. Research discovery contains build-specific module offsets and is not an end-user tool. Dependencies are not bundled.

Planned next: gameplay tests; gadget damage/KO; controller-scoped enemy freeze; challenge features if wanted; Batmobile mechanics after observing them. No armor, hit-box deletion, fly, XP, points, combo, global time, waypoint or puzzle bypass in v1.