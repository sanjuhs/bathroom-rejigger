# Toward photorealism

The first release prioritizes named, editable fixtures and a usable redesign workflow. It is a stylized reconstruction, not a photographic replica. More samples alone will not remove the simplified silhouettes or create missing material detail.

## First lighting and material study

Run `blender --background --factory-startup --threads 4 --python scripts/render_realism_study.py` from the project root.

This opens the existing master in a separate process and writes `blender/bathroom-realism-study.blend` and `renders/realism-study.png`. The master and the browser assets are preserved. The inspected first test revealed an artificial light reflection in the mirror; the follow-up removes that reflection artifact. The study uses the complete wall/ceiling enclosure, corridor illumination through an open entry, light at the visible bulb, a translucent window approximation, more accurate reflective materials, subtle surface bump and roughness variation, non-repeating floor mottling, and 128-sample Cycles rendering.

The light power and material parameters are artistic estimates. A neutral corridor backdrop provides reflection context; the area used to approximate corridor bounce is hidden from glossy rays to avoid a false studio-softbox reflection. The entry door is hidden to represent an open doorway. No claim of measured lighting or exact stains is made. Geometry remains largely the first-release geometry; some fixture silhouettes and small details still visibly need refinement.

## What matters most next

1. **Reference-matched geometry.** Refine the actual basin bowl/rim, toilet profile, tank, taps, hose connections, door edges, window recess and cabinet construction. Add small bevels, seams, mounts and believable wall contact. Good silhouettes matter more than simply increasing polygon counts.
2. **Material capture.** Photograph representative tile, grout, stone, painted door, metal and plastic surfaces straight-on, in even light. Build physically based color, roughness and normal/bump maps at a known scale. Remove lighting baked into source photos; retain the difference between material aging and cast shadow.
3. **Consistent light and reflections.** Match the bulb location, daylight entry and visible wall bounce. The first web release uses a generic environment for reflections; the mirror does not reflect the actual room. Add an actual planar mirror reflection and local reflection capture in the interactive version.
4. **A coherent camera.** Compare a fixed camera to one actual photo before judging realism. Match approximate position, height, field of view and exposure. Use full interior views as the realism benchmark; cutaways are useful for layout but inherently look like models.
5. **Two quality modes.** Keep a responsive editor with physically based materials and efficient lighting. Use Blender Cycles for high-quality stills of a selected design. Moving fixtures invalidates precomputed shadows, so baking everything into fixed textures is not enough for a live editor.

## What the owner can capture easily

No special camera, LiDAR scan or purchase is needed for the next pass. Existing references are enough to start.

- Use the phone's normal 1× lens. Keep lighting unchanged during a capture set and avoid portrait-mode blur, filters and digital zoom.
- Take overlapping eye-level pictures around the room, plus lower views revealing fixture sides and pipe connections. Include all four corners and the ceiling transitions.
- For the basin, toilet, geyser and cabinet, take a front view, side view and a three-quarter view where accessible.
- Take close-ups of a clean tile, an aged tile/grout joint, the dark stone, tap and hose hardware, and the mirror frame. Avoid glare obscuring the surface.
- Include one ruler or tape in the same plane as a tile or fixture. Even one reliable tile size and the basin width help calibrate proportions.
- For lighting comparison, capture a fixed view once with the room light on, and once with it off if there is enough ambient light. Never adjust or open electrical fittings.

Glossy white ceramic and mirrors make automatic reconstruction unreliable without manual cleanup; a scan can supplement an editable model, but does not replace it. Likewise, an AI-retouched still would not ensure that the movable 3D scene looks or behaves the same.

## Rendering references

- [Blender Cycles](https://docs.blender.org/manual/en/latest/render/cycles/introduction.html)
- [Principled physically based material](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html)
- [Three.js physical materials and their runtime cost](https://threejs.org/docs/pages/MeshPhysicalMaterial.html)

## Review of the saved study

The 1200 × 975, 128-sample follow-up render completed successfully and was visually inspected. The large false light disk in the mirror is removed. Reflections, material separation and contact shadows are stronger than the first-release view. This is still a material/lighting preview: the mirror reflects a simplified corridor, fixture geometry and labels remain stylized, and the floor wear is procedural rather than an exact match to a photograph. No real-time browser assets were replaced in this pass.
