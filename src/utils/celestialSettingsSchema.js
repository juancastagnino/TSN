import celestialModel from "../settings/celestial-model.json";

export const CELESTIAL_MODEL_SCHEMA_VERSION = 3;
export const CELESTIAL_SETTINGS_SCHEMA_VERSION = 3;
export const CELESTIAL_MODEL_ID = celestialModel.id;

const LEGACY_MODEL_IDS = new Set([
  "tychos-full-binary-system",
  "tychos-native-binary-system",
]);

const LEGACY_SETTING_NAMES_BY_ID = new Map([
  ["moon-node", new Set(["Moon Node"])],
  ["moon-plane", new Set(["Moon Plane"])],
  [
    "moon-deferent-a",
    new Set(["Moon deferent A", "Lunar Apsidal Deferent"]),
  ],
  [
    "moon-solar-eccentric",
    new Set([
      "Moon Solar-Coupled Eccentric",
      "Lunar 2D-M Eccentric Action",
    ]),
  ],
  ["eros-deferent-a", new Set(["Eros deferent A"])],
  ["eros-deferent-b", new Set(["Eros deferent B"])],
]);

const RETIRED_LUNAR_SETTING_IDS = new Set([
  "moon-anomalistic-tangent",
  "moon-solar-variation",
]);
const RETIRED_LUNAR_SETTING_NAMES = new Set([
  "Moon Anomalistic Tangential Frame",
  "Lunar Apsidal Tangential Action",
  "Moon Solar Variation",
  "Lunar Solar 2D Variation",
]);

const RETIRED_SOLAR_COMPANION_SETTING_IDS = new Set([
  "mercury-deferent-a",
  "mercury-deferent-b",
  "venus-deferent-a",
  "venus-deferent-b",
]);
const RETIRED_SOLAR_COMPANION_SETTING_NAMES = new Set([
  "Mercury deferent A",
  "Mercury deferent B",
  "Venus deferent A",
  "Venus deferent B",
]);

const DIRECT_PARENT_RELATIVE_IDS = new Set([
  "mars-deferent-e",
  "eros-deferent-a",
]);

export const SAVED_SETTING_PROPERTIES = [
  "id",
  "name",
  "size",
  "actualSize",
  "startPos",
  "speed",
  "rotationStart",
  "rotationSpeed",
  "tilt",
  "tiltb",
  "orbitRadius",
  "solarVariationRadius",
  "orbitCentera",
  "orbitCenterb",
  "orbitCenterc",
  "orbitTilta",
  "orbitTiltb",
  "amplitude",
  "phase",
  "axisX",
  "axisY",
  "axisZ",
];

const motionEntries = (owner) =>
  Object.entries(owner?.motion || {}).map(([component, setting]) => ({
    component,
    setting,
  }));

export const getCelestialOwners = (model = celestialModel) => [
  model.referenceFrame,
  ...(model.bodies || []),
].filter(Boolean);

export const getNativeCelestialSettings = (model = celestialModel) =>
  getCelestialOwners(model).flatMap((owner) =>
    motionEntries(owner).map(({ setting }) => ({ ...setting }))
  );

const nativeSettings = getNativeCelestialSettings();
const catalog = nativeSettings.map(({ id, name }) => ({ id, name }));
const catalogById = new Map(catalog.map((entry) => [entry.id, entry]));
const catalogByName = new Map(catalog.map((entry) => [entry.name, entry]));
LEGACY_SETTING_NAMES_BY_ID.forEach((names, id) => {
  const entry = catalogById.get(id);
  names.forEach((name) => catalogByName.set(name, entry));
});

const settingsArrayFromDocument = (document) => {
  if (Array.isArray(document)) return document;
  if (!document || typeof document !== "object") {
    throw new Error("Celestial settings must be an object or legacy array");
  }

  if (
    document.schemaVersion === CELESTIAL_MODEL_SCHEMA_VERSION &&
    Array.isArray(document.bodies) &&
    document.referenceFrame
  ) {
    if (document.id !== CELESTIAL_MODEL_ID) {
      throw new Error(
        `Settings target '${document.id}', expected '${CELESTIAL_MODEL_ID}'`
      );
    }
    return getNativeCelestialSettings(document);
  }

  // Compatibility with the former split schema and author settings exports.
  if (document.schemaVersion === 2 && Array.isArray(document.settings)) {
    if (document.modelId && !LEGACY_MODEL_IDS.has(document.modelId)) {
      throw new Error(`Unsupported legacy model '${document.modelId}'`);
    }
    return document.settings;
  }

  throw new Error("Unsupported celestial model/settings document");
};

export const normalizeCelestialSettings = (
  document,
  { requireComplete = true } = {}
) => {
  const rawSource = settingsArrayFromDocument(document);
  const source = rawSource
    .filter(
      (item) =>
        !RETIRED_LUNAR_SETTING_IDS.has(item?.id) &&
        !RETIRED_LUNAR_SETTING_NAMES.has(item?.name) &&
        !RETIRED_SOLAR_COMPANION_SETTING_IDS.has(item?.id) &&
        !RETIRED_SOLAR_COMPANION_SETTING_NAMES.has(item?.name)
    )
    .map((item) => ({ ...item }));
  const ids = new Set();
  const names = new Set();
  const settings = source.map((item, index) => {
    if (!item || typeof item !== "object") {
      throw new Error(`Invalid celestial setting at index ${index}`);
    }
    const catalogEntry = item.id
      ? catalogById.get(item.id)
      : catalogByName.get(item.name);
    if (!catalogEntry) {
      throw new Error(
        `Unknown celestial setting '${item.id || item.name || index}'`
      );
    }
    const legacyNames = LEGACY_SETTING_NAMES_BY_ID.get(catalogEntry.id);
    if (
      item.name &&
      item.name !== catalogEntry.name &&
      !legacyNames?.has(item.name)
    ) {
      throw new Error(
        `Setting '${catalogEntry.id}' must retain name '${catalogEntry.name}'`
      );
    }
    if (ids.has(catalogEntry.id) || names.has(catalogEntry.name)) {
      throw new Error(`Duplicate celestial setting '${catalogEntry.id}'`);
    }
    ids.add(catalogEntry.id);
    names.add(catalogEntry.name);
    return { ...item, id: catalogEntry.id, name: catalogEntry.name };
  });

  if (requireComplete) {
    const missing = catalog
      .filter((entry) => !ids.has(entry.id))
      .map((entry) => entry.id);
    if (missing.length) {
      throw new Error(`Missing celestial settings: ${missing.join(", ")}`);
    }
  }
  return settings;
};

export const buildSettingsIndex = (settings) => {
  const index = new Map();
  settings.forEach((setting) => {
    index.set(setting.id, setting);
    index.set(setting.name, setting);
  });
  return index;
};

export const findCelestialSetting = (settings, identifier) =>
  settings.find(
    (setting) => setting.id === identifier || setting.name === identifier
  );

export const mergeCelestialSettings = (current, importedDocument) => {
  const imported = normalizeCelestialSettings(importedDocument, {
    requireComplete: false,
  });
  const importedById = new Map(imported.map((setting) => [setting.id, setting]));
  return current.map((setting) => {
    const update = importedById.get(setting.id);
    if (
      update &&
      DIRECT_PARENT_RELATIVE_IDS.has(setting.id) &&
      Number(update.orbitRadius || 0) !== 0
    ) {
      throw new Error(
        `Setting '${setting.id}' uses the former absolute carrier format and cannot be merged into '${CELESTIAL_MODEL_ID}'`
      );
    }
    return update
      ? { ...setting, ...update, id: setting.id, name: setting.name }
      : setting;
  });
};

const filteredSetting = (item) => {
  const filtered = {};
  SAVED_SETTING_PROPERTIES.forEach((property) => {
    if (Object.prototype.hasOwnProperty.call(item, property)) {
      filtered[property] = item[property];
    }
  });
  return filtered;
};

/** Return a complete, directly reusable unified model document. */
export const serializeCelestialModel = (settings) => {
  const byId = buildSettingsIndex(settings);
  const document = JSON.parse(JSON.stringify(celestialModel));
  getCelestialOwners(document).forEach((owner) => {
    Object.entries(owner.motion || {}).forEach(([component, original]) => {
      const current = byId.get(original.id);
      if (!current) throw new Error(`Missing setting '${original.id}'`);
      owner.motion[component] = filteredSetting(current);
    });
  });
  return document;
};

// Compatibility name used by existing UI code and third-party extensions.
export const serializeCelestialSettings = serializeCelestialModel;

export const getCelestialEditorGroups = (settings) => {
  const byId = buildSettingsIndex(settings);
  const owners = new Map(
    getCelestialOwners().map((owner) => [owner.id, owner])
  );
  return celestialModel.editorGroups.map((group) => ({
    ...group,
    bodies: group.bodyIds.map((bodyId) => {
      const owner = owners.get(bodyId);
      if (!owner) {
        throw new Error(`Editor references unknown body '${bodyId}'`);
      }
      return {
        id: owner.id,
        name: owner.name,
        frames: (owner.editorFrames || []).map((frame) => ({
          ...frame,
          settings: frame.components.map((component) => {
            const setting = owner.motion[component];
            if (!setting) {
              throw new Error(
                `Editor frame '${frame.name}' references unknown component '${component}'`
              );
            }
            const current = byId.get(setting.id);
            if (!current) {
              throw new Error(`Editor references unknown setting '${setting.id}'`);
            }
            return { ...current, component };
          }),
        })),
        settings: motionEntries(owner).map(({ component, setting }) => {
          const current = byId.get(setting.id);
          if (!current) {
            throw new Error(`Editor references unknown setting '${setting.id}'`);
          }
          return { ...current, component };
        }),
      };
    }),
    settings: group.bodyIds.flatMap((bodyId) => {
      const owner = owners.get(bodyId);
      return motionEntries(owner).map(({ setting }) => byId.get(setting.id));
    }),
  }));
};

export const getCelestialSettingsCatalog = () =>
  catalog.map((entry) => ({ ...entry }));
