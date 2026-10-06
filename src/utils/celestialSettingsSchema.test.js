import nativeDocument from "../settings/celestial-settings.json";
import celestialModel from "../settings/celestial-model.json";
import {
  buildSettingsIndex,
  getCelestialEditorGroups,
  mergeCelestialSettings,
  normalizeCelestialSettings,
  serializeCelestialSettings,
} from "./celestialSettingsSchema";

const numericSnapshot = (settings) =>
  settings.map(({ id, name, ...values }) => ({ id, name, values }));

test("loads the complete versioned native settings document", () => {
  const settings = normalizeCelestialSettings(nativeDocument);
  expect(settings).toHaveLength(celestialModel.settingsCatalog.length);
  expect(new Set(settings.map((setting) => setting.id)).size).toBe(
    settings.length
  );
  expect(buildSettingsIndex(settings).get("mercury-plane").name).toBe(
    "Mercury Plane"
  );
});

test("imports a legacy flat settings array without changing its values", () => {
  const native = normalizeCelestialSettings(nativeDocument);
  const legacy = native.map(({ id, ...setting }) => setting);
  const imported = normalizeCelestialSettings(legacy);
  expect(numericSnapshot(imported)).toEqual(numericSnapshot(native));
});

test("round-trips native settings and preserves rotationStart", () => {
  const native = normalizeCelestialSettings(nativeDocument);
  const document = serializeCelestialSettings(native);
  expect(document.schemaVersion).toBe(2);
  expect(document.settings.find((setting) => setting.id === "earth").rotationStart).toBe(0);
  expect(numericSnapshot(normalizeCelestialSettings(document))).toEqual(
    numericSnapshot(native)
  );
});

test("applies partial legacy imports through stable IDs", () => {
  const native = normalizeCelestialSettings(nativeDocument);
  const merged = mergeCelestialSettings(native, [
    { name: "Mercury", startPos: 123.5 },
  ]);
  expect(buildSettingsIndex(merged).get("mercury").startPos).toBe(123.5);
  expect(buildSettingsIndex(merged).get("venus").startPos).toBe(
    buildSettingsIndex(native).get("venus").startPos
  );
});

test("preserves every direct parent-relative carrier field", () => {
  const native = normalizeCelestialSettings(nativeDocument);
  const serialized = serializeCelestialSettings(native);
  const roundTrip = buildSettingsIndex(normalizeCelestialSettings(serialized));

  [
    "mars-deferent-e",
    "mercury-deferent-a",
    "venus-deferent-a",
    "eros-deferent-a",
  ].forEach((id) => {
    const carrier = roundTrip.get(id);
    expect(carrier.orbitRadius).toBe(0);
    expect(carrier).toEqual(
      expect.objectContaining({
        relativeAnnualStart: expect.any(Number),
        relativeAnnualSpeed: expect.any(Number),
        relativeAnnualCosX: expect.any(Number),
        relativeAnnualCosY: expect.any(Number),
        relativeAnnualCosZ: expect.any(Number),
        relativeAnnualSinX: expect.any(Number),
        relativeAnnualSinY: expect.any(Number),
        relativeAnnualSinZ: expect.any(Number),
      })
    );
  });
});

test("rejects a former absolute carrier import in the full binary model", () => {
  const native = normalizeCelestialSettings(nativeDocument);
  expect(() =>
    mergeCelestialSettings(native, [
      {
        name: "Mercury deferent A",
        orbitRadius: 100,
        orbitCentera: -1.3,
      },
    ])
  ).toThrow(/former absolute carrier format/);
});

test("declares every setting exactly once in the hierarchy-aware editor", () => {
  const settings = normalizeCelestialSettings(nativeDocument);
  const grouped = getCelestialEditorGroups(settings).flatMap(
    (group) => group.settings
  );
  expect(grouped.map((setting) => setting.id).sort()).toEqual(
    settings.map((setting) => setting.id).sort()
  );
});

