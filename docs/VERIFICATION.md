# Verification — 29 September 2026

## Reference files

- Identified the contiguous AirDrop batch received at 12:15 local time: IMG_0368.MOV and IMG_0369.HEIC through IMG_0383.HEIC.
- Moved exactly these 16 files into `references/originals`; recomputed every SHA-256 hash after moving and again before publication.
- Reviewed all 15 upright photo previews and 21 sampled video frames from the 41.06-second clip.

## Blender

- Built with Blender 5.1.2 using a separate factory-startup background process. No writes were sent to the other agent's Blender MCP session.
- Generated 39 semantic object groups, a complete enclosed room master, seven alternative fixture exports and three camera renders.
- Visually inspected the cutaway, doorway and shower views; corrected the window recess, tile wear mapping and striped-wall proportions.
- Room dimensions use the user's approximate 2.40 × 1.50 × 2.60 m envelope. Model is interpretive and still needs a measured refinement pass.
- Imported a browser proposal with a moved basin, added oak vanity and changed floor into a separate `.blend` successfully (40 object groups). Color-only finish transfer is documented.

## Browser and build

- Production build passed. Five design validation tests passed, covering valid round trips, additional assets, missing objects, duplicate IDs, invalid transforms, unsupported finishes and oversized notes.
- Used the agent-browser tool to load the actual app and inspect rendered output and interactive controls. No browser runtime errors were reported.
- Verified moving basin X to 0.15 m, removing it, undoing removal, adding the oak vanity (39 → 40 groups), and changing the floor to sage.
- Pointer lock successfully engaged. Keyboard fallback supports automation/input sources that supply a key without a physical key code.

## Practical limits

No measured survey, drainage simulation, complete collision solver, exact commercial fixture specifications or multiplayer synchronization is provided. The editor uses approximate box overlap checks. Walkthrough is intended for desktop mouse/keyboard. Tiny details and surface aging are simplified. Material patterns in the browser are concept textures, not product selections.

- Verified duplication changed 39 → 40 objects and Undo returned to 39. Browser file-input import with an absolute path restored 40 objects and the sage floor.
- Verified forward walking changed camera position while keeping eye height at 1.62 m. Final npm dependency audit reported zero vulnerabilities.
