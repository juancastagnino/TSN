import React from "react";
import celestialModel from "../settings/celestial-model.json";
import celestialSettings from "../settings/celestial-settings.json";
import { normalizeCelestialSettings } from "../utils/celestialSettingsSchema";
import ErosSunRelativeOrbit from "./ErosSunRelativeOrbit";
import MercurySunRelativeOrbit from "./MercurySunRelativeOrbit";
import MoonOrbitalPlane from "./MoonOrbitalPlane";
import SunMarsBinaryTracker from "./SunMarsBinaryTracker";
import SunMarsRelativeOrbit from "./SunMarsRelativeOrbit";
import VenusSunRelativeOrbit from "./VenusSunRelativeOrbit";

export const CELESTIAL_NODE_KINDS = new Set([
  "group",
  "object",
  "moon-orbital-plane",
  "sun-mars-relative",
  "venus-sun-relative",
  "mercury-sun-relative",
  "eros-sun-relative",
  "sun-mars-binary-tracker",
]);

const modeAllows = (node, mode) =>
  !node.modes || node.modes.length === 0 || node.modes.includes(mode);

export const findCelestialNode = (id, node = celestialModel.root) => {
  if (node.id === id) return node;
  for (const child of node.children || []) {
    const found = findCelestialNode(id, child);
    if (found) return found;
  }
  return undefined;
};

export const validateCelestialModel = (model = celestialModel, settingIds) => {
  if (model.schemaVersion !== 2) {
    throw new Error(`Unsupported celestial model schema ${model.schemaVersion}`);
  }
  if (
    model.id !== "tychos-native-binary-system" ||
    model.settingsSchemaVersion !== 2
  ) {
    throw new Error("Celestial model identity or settings schema is invalid");
  }
  if (!model.root) throw new Error("Celestial model has no root node");
  if (
    !Array.isArray(model.settingsCatalog) ||
    !Array.isArray(model.editorGroups)
  ) {
    throw new Error("Celestial model has no settings catalog or editor groups");
  }

  const catalogIds = new Set();
  const catalogNames = new Set();
  model.settingsCatalog.forEach(({ id, name }) => {
    if (!id || !name) throw new Error("Invalid celestial settings catalog entry");
    if (catalogIds.has(id) || catalogNames.has(name)) {
      throw new Error(`Duplicate celestial settings catalog entry '${id}'`);
    }
    catalogIds.add(id);
    catalogNames.add(name);
  });
  model.editorGroups.forEach((group) =>
    group.settingIds.forEach((id) => {
      if (!catalogIds.has(id)) {
        throw new Error(
          `Editor group '${group.id}' references unknown setting '${id}'`
        );
      }
    })
  );

  const ids = new Set();
  const visit = (node, parentPath = "") => {
    const path = parentPath ? `${parentPath}/${node.id}` : node.id;
    if (!node.id) throw new Error(`Celestial node at ${parentPath} has no id`);
    if (ids.has(node.id)) throw new Error(`Duplicate celestial node id: ${node.id}`);
    ids.add(node.id);
    if (!CELESTIAL_NODE_KINDS.has(node.kind)) {
      throw new Error(`Unknown celestial node kind '${node.kind}' at ${path}`);
    }
    if ((node.kind === "group" || node.kind === "object") && !node.name) {
      throw new Error(`Celestial ${node.kind} at ${path} has no name`);
    }
    if (node.modes?.some((mode) => !["live", "plot"].includes(mode))) {
      throw new Error(`Invalid render mode at ${path}`);
    }
    if (settingIds) {
      const required =
        node.settingIds ||
        (node.kind === "object" ? [node.settingId || node.id] : []);
      required.forEach((id) => {
        if (!settingIds.has(id)) {
          throw new Error(`Unknown setting '${id}' referenced at ${path}`);
        }
      });
    }
    (node.children || []).forEach((child) => visit(child, path));
  };

  visit(model.root);
  return true;
};

validateCelestialModel(
  celestialModel,
  new Set(
    normalizeCelestialSettings(celestialSettings).map((setting) => setting.id)
  )
);

export const renderCelestialNode = (
  node,
  { ObjectComponent, mode },
  keyPath = node.id
) => {
  if (!modeAllows(node, mode)) return null;

  const children = (node.children || [])
    .map((child) =>
      renderCelestialNode(
        child,
        { ObjectComponent, mode },
        `${keyPath}/${child.id}`
      )
    )
    .filter(Boolean);
  const props = {
    key: keyPath,
    name: node.name,
    settingId: node.settingId || (node.kind === "object" ? node.id : undefined),
  };

  switch (node.kind) {
    case "group":
      return React.createElement("group", props, children);
    case "object":
      return React.createElement(ObjectComponent, props, children);
    case "moon-orbital-plane":
      return React.createElement(
        MoonOrbitalPlane,
        { ...props, live: mode === "live" },
        children
      );
    case "sun-mars-relative":
      return React.createElement(
        SunMarsRelativeOrbit,
        { ...props, plotMode: mode === "plot" },
        children
      );
    case "venus-sun-relative":
      return React.createElement(
        VenusSunRelativeOrbit,
        { ...props, plotMode: mode === "plot" },
        children
      );
    case "mercury-sun-relative":
      return React.createElement(
        MercurySunRelativeOrbit,
        { ...props, plotMode: mode === "plot" },
        children
      );
    case "eros-sun-relative":
      return React.createElement(
        ErosSunRelativeOrbit,
        { ...props, plotMode: mode === "plot" },
        children
      );
    case "sun-mars-binary-tracker":
      return React.createElement(SunMarsBinaryTracker, props);
    default:
      throw new Error(`Unsupported celestial node kind: ${node.kind}`);
  }
};

const DeclarativeCelestialModel = ({ ObjectComponent, mode }) => {
  if (!ObjectComponent) throw new Error("Declarative model needs an object component");
  if (!["live", "plot"].includes(mode)) {
    throw new Error(`Unsupported declarative model mode: ${mode}`);
  }
  return renderCelestialNode(celestialModel.root, { ObjectComponent, mode });
};

export default DeclarativeCelestialModel;
