import celestialModel from "../settings/celestial-model.json";
import {
  buildSettingsIndex,
  getCelestialEditorGroups,
  getCelestialSettingsCatalog,
  mergeCelestialSettings,
  normalizeCelestialSettings,
  serializeCelestialSettings,
} from "./celestialSettingsSchema";

const numericSnapshot = (settings) =>
  settings.map(({ id, name, ...values }) => ({ id, name, values }));

test("loads the complete unified native model", () => {
  const settings = normalizeCelestialSettings(celestialModel);
  expect(settings).toHaveLength(getCelestialSettingsCatalog().length);
  expect(new Set(settings.map((setting) => setting.id)).size).toBe(
    settings.length
  );
  expect(buildSettingsIndex(settings).get("mercury-plane").name).toBe(
    "Mercury Plane"
  );
});

test("imports a legacy flat settings array without changing its values", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const legacy = native.map(({ id, ...setting }) => setting);
  const imported = normalizeCelestialSettings(legacy);
  expect(numericSnapshot(imported)).toEqual(numericSnapshot(native));
});

test("round-trips a complete unified model and preserves rotationStart", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const document = serializeCelestialSettings(native);
  expect(document.schemaVersion).toBe(3);
  expect(
    document.bodies.find((body) => body.id === "earth").motion.orbit
      .rotationStart
  ).toBe(0);
  expect(numericSnapshot(normalizeCelestialSettings(document))).toEqual(
    numericSnapshot(native)
  );
});

test("applies partial legacy imports through stable IDs", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const merged = mergeCelestialSettings(native, [
    { name: "Mercury", startPos: 123.5 },
  ]);
  expect(buildSettingsIndex(merged).get("mercury").startPos).toBe(123.5);
  expect(buildSettingsIndex(merged).get("venus").startPos).toBe(
    buildSettingsIndex(native).get("venus").startPos
  );
});

test("accepts former Moon component names while normalizing to the new frame vocabulary", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const merged = mergeCelestialSettings(native, [
    { name: "Moon Node", speed: -0.4 },
    { name: "Moon Plane", orbitTiltb: -5.3 },
    { name: "Moon deferent A", startPos: 166 },
  ]);
  const index = buildSettingsIndex(merged);
  expect(index.get("moon-node")).toEqual(
    expect.objectContaining({ name: "Lunar Nodal Deferent", speed: -0.4 })
  );
  expect(index.get("moon-plane")).toEqual(
    expect.objectContaining({ name: "Lunar Plane Deferent", orbitTiltb: -5.3 })
  );
  expect(index.get("moon-deferent-a")).toEqual(
    expect.objectContaining({ name: "Lunar Apsidal Geometry", startPos: 166 })
  );
});

test("ignores retired lunar components when loading former settings", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const merged = mergeCelestialSettings(native, [
    {
      id: "moon-anomalistic-tangent",
      name: "Lunar Apsidal Tangential Action",
      orbitRadius: 0.019,
    },
    {
      id: "moon-solar-variation",
      name: "Lunar Solar 2D Variation",
      orbitRadius: 0.003,
    },
  ]);
  const index = buildSettingsIndex(merged);
  expect(index.get("moon-deferent-a").tangentialRadius).toBeUndefined();
  expect(index.get("moon-anomalistic-tangent")).toBeUndefined();
  expect(index.get("moon-solar-variation")).toBeUndefined();
});

test("round-trips both solar-coupled lunar amplitudes in one setting", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const serialized = serializeCelestialSettings(native);
  const roundTrip = buildSettingsIndex(normalizeCelestialSettings(serialized));
  expect(roundTrip.get("moon-solar-eccentric")).toEqual(
    expect.objectContaining({
      orbitRadius: "-0.0055",
      solarVariationRadius: "0.002168",
    })
  );
});

test("retains only active direct carriers and Eros's declared annual geometry", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const serialized = serializeCelestialSettings(native);
  const roundTrip = buildSettingsIndex(normalizeCelestialSettings(serialized));

  const marsCarrier = roundTrip.get("mars-deferent-e");
  expect(marsCarrier.orbitRadius).toBe(0);
  expect(marsCarrier.relativeAnnualSpeed).toBeUndefined();
  expect(roundTrip.get("mercury-deferent-a")).toBeUndefined();
  expect(roundTrip.get("mercury-deferent-b")).toBeUndefined();
  expect(roundTrip.get("venus-deferent-a")).toBeUndefined();
  expect(roundTrip.get("venus-deferent-b")).toBeUndefined();
  expect(roundTrip.get("mercury-deferent")).toEqual(
    expect.objectContaining({ speed: -2 * Math.PI })
  );
  expect(roundTrip.get("venus-deferent")).toEqual(
    expect.objectContaining({ speed: -2 * Math.PI })
  );
  expect(roundTrip.get("eros-deferent-a")).not.toEqual(
    expect.objectContaining({
      relativeAnnualSpeed: expect.any(Number),
    })
  );
  expect(roundTrip.get("eros-annual-centre-oscillation")).toEqual(
    expect.objectContaining({
      amplitude: expect.any(Number),
      phase: expect.any(Number),
      speed: expect.any(Number),
      axisY: expect.any(Number),
    })
  );
});

test("ignores retired Venus and Mercury carrier settings on import", () => {
  const native = normalizeCelestialSettings(celestialModel);
  const merged = mergeCelestialSettings(native, [
    {
      name: "Mercury deferent A",
      orbitRadius: 100,
      orbitCentera: -1.3,
    },
  ]);
  expect(merged).toEqual(native);
});

test("declares every motion component exactly once in the body-aware editor", () => {
  const settings = normalizeCelestialSettings(celestialModel);
  const grouped = getCelestialEditorGroups(settings).flatMap(
    (group) => group.settings
  );
  expect(grouped.map((setting) => setting.id).sort()).toEqual(
    settings.map((setting) => setting.id).sort()
  );
});
