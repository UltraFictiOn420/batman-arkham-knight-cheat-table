# Batman Arkham Knight — Original Cheat Table

Original 64-bit Steam `BatmanAK.exe` single-player Cheat Engine project. **v1 is a first test build, not a verified release.** No console setup or game executable patches. No third-party Knight table was imported.

## Organization

- `tables/latest-test/v1/`: first test table.
- `development/work/`: original Lua, builder, read-only discovery, and live-read/simulated-write tests.
- `docs/version-notes/v1.md`: feature descriptions, caveats and verification scope.
- `docs/STATUS_AND_TESTING.md`, `docs/SAFETY_AND_SETUP.md`, `docs/PROVENANCE.md`.
- `catalog/features.json`: categories, code type, purpose and completion/testing status.
- `CHECKSUMS.sha256`: artifact integrity.

Includes living-player health refill, melee enemy HP caps, player-inventory grapple/Batarang range edits, J/K/L save/teleport/undo, F1-F4 upward teleports. Main -/= toggle damage modes. Gadget knockout damage, enemy freeze, challenge features and Batmobile cheats are planned, not implemented or promised working.

Initialize in loaded single-player gameplay and test one toggle at a time. Back up saves. Every feature remains [Test] until the user's gameplay confirmation. No license selected yet; private preservation archive only.