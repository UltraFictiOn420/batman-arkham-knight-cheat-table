# Safety and setup

Back up saves. Use only in single-player Steam `BatmanAK.exe` x64, never multiplayer/competitive/anti-cheat sessions. Load one table version, initialize in actual gameplay, then test individual entries. Review embedded Lua before allowing execution. No developer-console commands required.

Health refills living Batman, not immunity to instant/scripted death. Super Damage reduces eligible loaded enemy HP to a tenth of maximum; One-Hit reduces HP to 1. Disabling does not undo lost enemy HP. Disable during tutorials, scripted scenes and bosses until tested. These are NOT yet verified gadget knockout modifiers.

Reach adjusts player inventory fields only; it cannot create grapple targets, bypass visibility or stream unloaded locations. Teleports work only in walking/falling states in the same pawn/world. They do not check walls or safe ground. Save a safe point with J; K teleports, L undoes/redoes. F1-F4 raise by 1/2/5/10 body heights. Avoid vehicle, grapple, ledge and cutscene transitions. Batmobile support is not included.

Development sources are research tools, not required for table use. Do not upload binaries, game assets, full memory dumps, savegames, credentials or dependency packages.