# Bathroom Rejigger — project objective

Build an editable, walkable reconstruction of the current bathroom for Swati, the architect, then use it to explore a neater and better-organized redesign. Preserve an identifiable existing-condition baseline and let proposed layouts be saved separately.

## Deliverables

- [x] Consolidate the latest AirDrop batch: 15 photographs and one 41-second video, with SHA-256 integrity records.
- [x] Record the visible bathroom contents and the reference evidence.
- [x] Create and visually verify an editable Blender reconstruction and rendered views.
- [x] Provide a browser-based 3D walkthrough and layout editor.
- [x] Allow object placement, rotation, removal, replacement, and tile finish exploration.
- [x] Include alternative toilets, basins, showers, geysers, cabinetry, and plug points.
- [x] Save/share proposed layouts and preserve the original scene.
- [x] Publish a public GitHub backup under the MIT license.

## Accuracy and design constraints

This initial reconstruction is interpreted from images, not photogrammetric or measured survey data. The starting room envelope is **2.40 × 1.50 × 2.60 m**, with **0.30 m floor tiles**, all provisional. Room dimensions were estimated by the user: length ±0.10 m; width and height not yet tape-verified. Visible object shapes and placement are approximate; hidden geometry and labels are simplified. These values are editable in `scripts/build_bathroom.py`.

The floor is modeled level because slope, drain elevation, waterproofing buildup, pipe routes, circuit ratings, and structural constraints cannot be established from the photos. Layout editing is a design conversation tool. Swati should verify dimensions, drainage gradients, fixture clearances, and service locations before final specification.

## Next survey pass

1. Measure the two inside floor spans between finished wall faces.
2. Measure one tile and the door opening width.
3. If easy to reach, measure basin width and its height above the floor.
4. Swati can check ceiling height, drain position, levels and service constraints on site.

A tape measure is sufficient. A phone measurement app can provide an interim estimate. Nothing here requires climbing or dismantling fixtures.

## Working approach

Keep reproducible Python modeling scripts, a complete `.blend` master, portable GLB assets, renders, original references, and the editor together. Use a separate background Blender process so the other agent's live session is unaffected. The existing layout is always recoverable with Reset; designs can be exported to JSON and re-imported.

## First working version

Completed on 29 September 2026. Public source and original references: https://github.com/sanjuhs/bathroom-rejigger. Browser studio: https://sanjuhs.github.io/bathroom-rejigger/. The next refinement milestone is a measured survey and Swati’s layout feedback.
