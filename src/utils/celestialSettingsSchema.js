import celestialModel from "../settings/celestial-model.json";

export const CELESTIAL_SETTINGS_SCHEMA_VERSION = 2;
export const CELESTIAL_MODEL_SCHEMA_VERSION = 2;
export const CELESTIAL_MODEL_ID = celestialModel.id;

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
  "orbitCentera",
  "orbitCenterb",
  "orbitCenterc",
  "orbitTilta",
  "orbitTiltb",
];

const catalogById = new Map(
  celestialModel.settingsCatalog.map((entry) => [entry.id, entry])
);
const catalogByName = new Map(
  celestialModel.settingsCatalog.map((entry) => [entry.name, entry])
);

const settingsArrayFromDocument = (document) => {
  if (Array.isArray(document)) return document;
  if (!document || typeof document !== "object") {
    throw new Error("Celestial settings must be an object or legacy array");
  }
  if (document.schemaVersion !== CELESTIAL_SETTINGS_SCHEMA_VERSION) {
    throw new Error(
      `Unsupported celestial settings schema ${document.schemaVersion}`
    );
  }
  if (document.modelSchemaVersion !== CELESTIAL_MODEL_SCHEMA_VERSION) {
    throw new Error(
      `Settings require model schema ${document.modelSchemaVersion}, expected ${CELESTIAL_MODEL_SCHEMA_VERSION}`
    );
  }
  if (document.modelId !== CELESTIAL_MODEL_ID) {
    throw new Error(
      `Settings target '${document.modelId}', expected '${CELESTIAL_MODEL_ID}'`
    );
  }
  if (!Array.isArray(document.settings)) {
    throw new Error("Versioned celestial settings have no settings array");
  }
  return document.settings;
};

export const normalizeCelestialSettings = (
  document,
  { requireComplete = true } = {}
) => {
  const source = settingsArrayFromDocument(document);
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
    if (item.name && item.name !== catalogEntry.name) {
      throw new Error(
        `Setting '${catalogEntry.id}' must retain legacy name '${catalogEntry.name}'`
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
    const missing = celestialModel.settingsCatalog
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
    return update
      ? { ...setting, ...update, id: setting.id, name: setting.name }
      : setting;
  });
};

export const serializeCelestialSettings = (settings) => ({
  schemaVersion: CELESTIAL_SETTINGS_SCHEMA_VERSION,
  modelSchemaVersion: CELESTIAL_MODEL_SCHEMA_VERSION,
  modelId: CELESTIAL_MODEL_ID,
  settings: settings.map((item) => {
    const filtered = {};
    SAVED_SETTING_PROPERTIES.forEach((property) => {
      if (Object.prototype.hasOwnProperty.call(item, property)) {
        filtered[property] = item[property];
      }
    });
    return filtered;
  }),
});

export const getCelestialEditorGroups = (settings) => {
  const byId = buildSettingsIndex(settings);
  return celestialModel.editorGroups.map((group) => ({
    ...group,
    settings: group.settingIds.map((id) => {
      const setting = byId.get(id);
      if (!setting) throw new Error(`Editor references unknown setting '${id}'`);
      return setting;
    }),
  }));
};

export const getCelestialSettingsCatalog = () =>
  celestialModel.settingsCatalog.map((entry) => ({ ...entry }));
