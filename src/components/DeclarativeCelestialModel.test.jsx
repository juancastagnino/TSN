import React from "react";
import celestialModel from "../settings/celestial-model.json";
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
  if (node.kind === "object" || node.kind === "reference-frame") {
    result.push(node.name);
  }
  (node.children || []).forEach((child) => objectNames(child, mode, result));
  return result;
};

const pathTo = (targetId, node = celestialModel.renderTree, parents = []) => {
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
    normalizeCelestialSettings(celestialModel).map((setting) => setting.id)
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

test("keeps Pluto eccentric geometry active without rendering its helper orbit", () => {
  const eccentric = findCelestialNode("pluto-eccentric");
  const pluto = celestialModel.bodies.find((body) => body.id === "pluto");
  expect(eccentric.kind).toBe("pluto-eccentric-frame");
  expect(eccentric.renderOrbit).toBe(false);
  expect(eccentric.children.map((child) => child.id)).toEqual(["pluto"]);
  expect(pluto.motion.eccentric.orbitRadius).toBe("134.260927266641");
  expect(pluto.motion.eccentric.speed).toBe("0.0506606");
  expect(pluto.motion.eccentricCounterrotation).toBeUndefined();
  expect(pluto.motion.eccentric.children).toBeUndefined();
});

test("declares real bodies once and keeps motion stages inside their owners", () => {
  const moon = celestialModel.bodies.find((body) => body.id === "moon");
  const mars = celestialModel.bodies.find((body) => body.id === "mars");
  const venus = celestialModel.bodies.find((body) => body.id === "venus");
  const mercury = celestialModel.bodies.find((body) => body.id === "mercury");
  expect(moon.parentId).toBe("earth");
  expect(Object.keys(moon.motion)).toEqual([
    "node",
    "plane",
    "deferentA",
    "equant",
    "solarCoupledEccentric",
    "orbit",
  ]);
  expect(moon.motion.deferentA.tangentialRadius).toBeUndefined();
  expect(moon.motion.plane.speed).toBe("0");
  expect(moon.motion.deferentA.orbitRadius).toBe("0.014073729727223986");
  expect(moon.motion.equant.orbitRadius).toBe("0.014073729727223986");
  expect(moon.motion.solarCoupledEccentric.orbitRadius).toBe("-0.0055");
  expect(moon.motion.solarCoupledEccentric.solarVariationRadius).toBe(
    "0.002168"
  );
  expect(moon.motion.solarVariation).toBeUndefined();
  expect(moon.motion.anomalisticTangent).toBeUndefined();
  expect(findCelestialNode("moon-deferent-a").kind).toBe("motion-stage");
  expect(findCelestialNode("moon-solar-eccentric-frame")).toEqual(
    expect.objectContaining({
      kind: "moon-solar-eccentric",
      targetName: "Moon",
    })
  );
  expect(findCelestialNode("moon-apsidal-equant-frame")).toEqual(
    expect.objectContaining({
      kind: "moon-apsidal-equant",
      settingId: "moon-apsidal-equant",
      targetName: "Moon",
    })
  );
  expect(findCelestialNode("moon-orbital-frame").name).toBe(
    "Lunar Nodal / Plane Frame"
  );
  expect(findCelestialNode("moon-deferent-a").name).toBe(
    "Lunar Apsidal Frame"
  );
  expect(findCelestialNode("moon-solar-eccentric-frame").name).toBe(
    "Solar-Coupled Lunar Frame"
  );
  expect(mars.parentId).toBe("sun");
  expect(Object.keys(mars.motion)).toEqual([
    "binaryAnnualFrame",
    "longPeriodDeferent",
    "orbit",
  ]);
  expect(mars.motion.binaryAnnualFrame.id).toBe("mars-deferent-e");
  expect(mars.motion.binaryAnnualFrame.name).toBe("Mars Binary Annual Frame");
  expect(mars.motion.longPeriodDeferent.id).toBe("mars-deferent-s");
  const eros = celestialModel.bodies.find((body) => body.id === "eros");
  expect(Object.keys(eros.motion)).toEqual([
    "sunRelativeAnnualFrame",
    "annualCentreOscillation",
    "localDeferent",
    "orbit",
  ]);
  expect(eros.motion.sunRelativeAnnualFrame.id).toBe("eros-deferent-a");
  expect(eros.motion.annualCentreOscillation.id).toBe(
    "eros-annual-centre-oscillation"
  );
  expect(eros.motion.localDeferent.id).toBe("eros-deferent-b");
  expect(venus.parentId).toBe("sun");
  expect(Object.keys(venus.motion)).toEqual(["deferent", "plane", "orbit"]);
  expect(mercury.parentId).toBe("sun");
  expect(Object.keys(mercury.motion)).toEqual(["deferent", "plane", "orbit"]);
  expect(celestialModel.bodies.some((body) => body.id.includes("deferent"))).toBe(
    false
  );
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
    "Mars Binary Geometry",
    "Mars Binary Companion Branch",
    "Mars",
  ]);
  expect(pathTo("venus")).toEqual([
    ...prefix,
    "Venus deferent",
    "Venus Plane",
    "Venus",
  ]);
  expect(pathTo("mercury")).toEqual([
    ...prefix,
    "Mercury deferent",
    "Mercury Plane",
    "Mercury",
  ]);
  expect(pathTo("eros")).toEqual([
    ...prefix,
    "Eros Sun-Relative Geometry",
    "Eros Solar Asteroid Branch",
    "Eros",
  ]);
});

test("keeps live-only physical Moon and tracker nodes out of the plot model", () => {
  const liveObjects = objectNames(celestialModel.renderTree, "live");
  const plotObjects = objectNames(celestialModel.renderTree, "plot");

  expect(liveObjects).toContain("Actual Moon");
  expect(liveObjects).not.toContain("Actual Moon deferent A");
  expect(plotObjects).not.toContain("Actual Moon");

  const liveTree = renderCelestialNode(celestialModel.renderTree, {
    ObjectComponent: StubObject,
    mode: "live",
  });
  const plotTree = renderCelestialNode(celestialModel.renderTree, {
    ObjectComponent: StubObject,
    mode: "plot",
  });
  expect(descendantNames(liveTree)).toContain("Sun-Mars Binary Tracker");
  expect(descendantNames(plotTree)).not.toContain("Sun-Mars Binary Tracker");
});

test("declares the same physical object order used by the accepted JSX trees", () => {
  expect(objectNames(celestialModel.renderTree, "live")).toEqual([
    "SystemCenter",
    "Earth",
    "Moon",
    "Actual Moon",
    "Sun",
    "Halleys",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "Mars",
    "Phobos",
    "Deimos",
    "Venus",
    "Mercury",
    "Eros",
  ]);
  expect(objectNames(celestialModel.renderTree, "plot")).toEqual([
    "SystemCenter",
    "Earth",
    "Moon",
    "Sun",
    "Halleys",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "Mars",
    "Phobos",
    "Deimos",
    "Venus",
    "Mercury",
    "Eros",
  ]);
});
