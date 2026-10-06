import React from "react";
import celestialModel from "../settings/celestial-model.json";
import celestialSettings from "../settings/celestial-settings.json";
import { normalizeCelestialSettings } from "../utils/celestialSettingsSchema";
import {
  findCelestialNode,
  renderCelestialNode,
  validateCelestialModel,
} from "./DeclarativeCelestialModel";

const StubObject = () => null;

const childrenOf = (element) =>
  React.Children.toArray(element?.props?.children).filter(React.isValidElement);

const descendantNames = (element) => {
  const names = [];
  const visit = (node) => {
    if (!React.isValidElement(node)) return;
    if (node.props.name) names.push(node.props.name);
    childrenOf(node).forEach(visit);
  };
  visit(element);
  return names;
};

const objectNames = (node, mode, result = []) => {
  if (node.modes && !node.modes.includes(mode)) return result;
  if (node.kind === "object") result.push(node.name);
  (node.children || []).forEach((child) => objectNames(child, mode, result));
  return result;
};

const pathTo = (targetId, node = celestialModel.root, parents = []) => {
  const path = [...parents, node.name];
  if (node.id === targetId) return path;
  for (const child of node.children || []) {
    const found = pathTo(targetId, child, path);
    if (found) return found;
  }
  return undefined;
};

test("validates every declarative node and settings dependency", () => {
  const settingIds = new Set(
    normalizeCelestialSettings(celestialSettings).map((setting) => setting.id)
  );
  expect(validateCelestialModel(celestialModel, settingIds)).toBe(true);
});

test("declares one shared Sun-Mars hierarchy with the accepted branches", () => {
  const binary = findCelestialNode("sun-mars-binary");
  expect(binary.name).toBe("Sun-Mars Binary Frame");
  expect(findCelestialNode("mars").role).toBe("junior-companion");
  expect(findCelestialNode("venus").role).toBe("senior-solar-companion");
  expect(findCelestialNode("mercury").role).toBe("junior-solar-companion");
  expect(findCelestialNode("eros").role).toBe("sun-hosted-asteroid");
  expect(findCelestialNode("phobos").role).toBe("mars-satellite");
  expect(findCelestialNode("deimos").role).toBe("mars-satellite");
});

test("preserves the accepted parent path for every reparented body", () => {
  const prefix = [
    "TYCHOS Celestial Model",
    "SystemCenter",
    "Earth",
    "Sun-Mars Binary Frame",
    "Sun Primary Branch",
    "Sun deferent",
    "Sun",
  ];
  expect(pathTo("mars")).toEqual([
    ...prefix,
    "Mars Native Relative Components",
    "Mars Junior Companion Branch",
    "Mars",
  ]);
  expect(pathTo("venus")).toEqual([
    ...prefix,
    "Venus Native Relative Frame",
    "Venus Senior Solar Companion Branch",
    "Venus",
  ]);
  expect(pathTo("mercury")).toEqual([
    ...prefix,
    "Mercury Native Relative Frame",
    "Mercury Junior Solar Companion Branch",
    "Mercury",
  ]);
  expect(pathTo("eros")).toEqual([
    ...prefix,
    "Eros Native Relative Frame",
    "Eros Solar Asteroid Branch",
    "Eros",
  ]);
});

test("keeps live-only physical Moon and tracker nodes out of the plot model", () => {
  const liveObjects = objectNames(celestialModel.root, "live");
  const plotObjects = objectNames(celestialModel.root, "plot");

  expect(liveObjects).toEqual(
    expect.arrayContaining(["Actual Moon deferent A", "Actual Moon"])
  );
  expect(plotObjects).not.toEqual(
    expect.arrayContaining(["Actual Moon deferent A", "Actual Moon"])
  );

  const liveTree = renderCelestialNode(celestialModel.root, {
    ObjectComponent: StubObject,
    mode: "live",
  });
  const plotTree = renderCelestialNode(celestialModel.root, {
    ObjectComponent: StubObject,
    mode: "plot",
  });
  expect(descendantNames(liveTree)).toContain("Sun-Mars Binary Tracker");
  expect(descendantNames(plotTree)).not.toContain("Sun-Mars Binary Tracker");
});

test("declares the same physical object order used by the accepted JSX trees", () => {
  expect(objectNames(celestialModel.root, "live")).toEqual([
    "SystemCenter",
    "Earth",
    "Moon deferent A",
    "Moon",
    "Actual Moon deferent A",
    "Actual Moon",
    "Sun deferent",
    "Sun",
    "Halleys deferent",
    "Halleys",
    "Jupiter deferent",
    "Jupiter",
    "Saturn deferent",
    "Saturn",
    "Uranus deferent",
    "Uranus",
    "Neptune deferent",
    "Neptune",
    "Pluto deferent",
    "Pluto",
    "Mars",
    "Phobos",
    "Deimos",
    "Venus",
    "Mercury",
    "Eros",
  ]);
  expect(objectNames(celestialModel.root, "plot")).toEqual([
    "SystemCenter",
    "Earth",
    "Moon deferent A",
    "Moon",
    "Sun deferent",
    "Sun",
    "Halleys deferent",
    "Halleys",
    "Jupiter deferent",
    "Jupiter",
    "Saturn deferent",
    "Saturn",
    "Uranus deferent",
    "Uranus",
    "Neptune deferent",
    "Neptune",
    "Pluto deferent",
    "Pluto",
    "Mars",
    "Phobos",
    "Deimos",
    "Venus",
    "Mercury",
    "Eros",
  ]);
});
