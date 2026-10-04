import { Object3D, Vector3 } from "three";
import settings from "../settings/celestial-settings.json";
import { buildSettingsIndex, normalizeCelestialSettings } from "../utils/celestialSettingsSchema";
import {
  createErosSunRelativeComponents,
  updateErosSunRelativeComponents,
} from "./ErosSunRelativeOrbit";

const D2R = Math.PI / 180;
const byName = buildSettingsIndex(normalizeCelestialSettings(settings));
const number = (setting, key) => Number(setting[key] || 0);

const appendOrbitNode = (parent, setting, position) => {
  const container = new Object3D();
  container.position.set(
    number(setting, "orbitCentera"),
    number(setting, "orbitCenterc"),
    number(setting, "orbitCenterb")
  );
  container.rotation.set(
    number(setting, "orbitTilta") * D2R,
    0,
    number(setting, "orbitTiltb") * D2R
  );
  const orbit = new Object3D();
  orbit.rotation.y =
    number(setting, "speed") * position -
    number(setting, "startPos") * D2R;
  const pivot = new Object3D();
  pivot.position.x = number(setting, "orbitRadius");
  parent.add(container);
  container.add(orbit);
  orbit.add(pivot);
  return pivot;
};

const chainPosition = (names, position) => {
  const root = new Object3D();
  let parent = root;
  names.forEach((name) => {
    parent = appendOrbitNode(parent, byName.get(name), position);
  });
  root.updateMatrixWorld(true);
  return parent.getWorldPosition(new Vector3());
};

const reconstructedRelative = (position) => {
  const components = updateErosSunRelativeComponents(
    createErosSunRelativeComponents(),
    byName,
    position
  );
  return components.centreDifference
    .clone()
    .add(components.annualCarrierMismatch)
    .add(components.deferentBStage)
    .add(
      chainPosition(["Eros"], position).applyMatrix4(
        components.mainBasis
      )
    );
};

const legacyRelative = (position) =>
  chainPosition(
    ["Eros deferent A", "Eros deferent B", "Eros"],
    position
  ).sub(chainPosition(["Sun deferent", "Sun"], position));

test.each([-0.001, 0, 0.25, 3.75, 26])(
  "reconstructs the legacy Sun-relative Eros vector at position %p",
  (position) => {
    expect(
      reconstructedRelative(position).distanceTo(legacyRelative(position))
    ).toBeLessThan(1e-10);
  }
);

test("matches the legacy relative vector over a dense multi-century grid", () => {
  let maximumDifference = 0;
  for (let index = 0; index <= 128; index += 1) {
    const position = -100 + (200 * index) / 128;
    maximumDifference = Math.max(
      maximumDifference,
      reconstructedRelative(position).distanceTo(legacyRelative(position))
    );
  }
  expect(maximumDifference).toBeLessThan(1e-10);
});

test("retains the non-zero mismatch between the tilted annual carriers", () => {
  const components = updateErosSunRelativeComponents(
    createErosSunRelativeComponents(),
    byName,
    4.25
  );
  const erosA = byName.get("Eros deferent A");
  const sun = byName.get("Sun");

  expect(number(erosA, "orbitRadius")).toBe(number(sun, "orbitRadius"));
  expect(components.annualCarrierMismatch.length()).toBeGreaterThan(1);
});
