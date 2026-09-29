export const SCHEMA_VERSION = 1;
export function validateDesign(data, existingIds, catalogIds) {
  if (
    !data ||
    data.schema !== SCHEMA_VERSION ||
    !Array.isArray(data.objects) ||
    data.objects.length > 250
  )
    throw new Error("This is not a supported Bathroom Rejigger design.");
  const seen = new Set();
  for (const o of data.objects) {
    if (!o || typeof o.id !== "string" || seen.has(o.id))
      throw new Error("Duplicate or missing object ID.");
    seen.add(o.id);
    if (
      o.asset
        ? !catalogIds.has(o.asset) || existingIds.has(o.id)
        : !existingIds.has(o.id)
    )
      throw new Error("Unknown object or fixture asset.");
    if (
      !Array.isArray(o.p) ||
      o.p.length !== 3 ||
      o.p.some((v) => !Number.isFinite(v) || Math.abs(v) > 20)
    )
      throw new Error("Invalid object position.");
    if (
      !Array.isArray(o.q) ||
      o.q.length !== 4 ||
      o.q.some((v) => !Number.isFinite(v)) ||
      Math.abs(Math.hypot(...o.q) - 1) > 0.01
    )
      throw new Error("Invalid object rotation.");
    if (typeof o.visible !== "boolean") throw new Error("Invalid visibility.");
  }
  if ([...existingIds].some((id) => !seen.has(id)))
    throw new Error("Design is missing an original object.");
  if (typeof data.notes !== "string" || data.notes.length > 20000)
    throw new Error("Invalid notes.");
  const validFinishes = new Set([
    "existing",
    "limestone",
    "sage",
    "terrazzo",
    "terracotta",
  ]);
  if (
    !data.finishes ||
    ["floor", "walls", "feature"].some(
      (s) => !validFinishes.has(data.finishes[s]),
    )
  )
    throw new Error("Invalid surface finish.");
  return data;
}
