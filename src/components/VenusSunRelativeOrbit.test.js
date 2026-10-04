import { Object3D, Vector3 } from "three";
import settings from "../settings/celestial-settings.json";
import { buildSettingsIndex, normalizeCelestialSettings } from "../utils/celestialSettingsSchema";
import {
  createVenusSunRelativeComponents,
  updateVenusSunRelativeComponents,
} from "./VenusSunRelativeOrbit";

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

test.each([-0.001, 0, 0.25, 3.75, 26])(
  "reconstructs the legacy Sun-relative Venus vector at position %p",
  (position) => {
    const components = updateVenusSunRelativeComponents(
      createVenusSunRelativeComponents(),
      byName,
      position
    );
    const localVenus = chainPosition(["Venus"], position);
    const reconstructed = components.centreDifference
      .clone()
      .add(components.annualCarrierMismatch)
      .add(components.deferentBStage)
      .add(components.planeStage)
      .add(localVenus.applyMatrix4(components.mainBasis));
    const legacy = chainPosition(
      ["Venus deferent A", "Venus deferent B", "Venus Plane", "Venus"],
      position
    ).sub(chainPosition(["Sun deferent", "Sun"], position));

    expect(reconstructed.distanceTo(legacy)).toBeLessThan(1e-10);
  }
);

test("matches the legacy relative vector over a dense multi-century grid", () => {
  let maximumDifference = 0;
  for (let index = 0; index <= 128; index += 1) {
    const position = -100 + (200 * index) / 128;
    const components = updateVenusSunRelativeComponents(
      createVenusSunRelativeComponents(),
      byName,
      position
    );
    const reconstructed = components.centreDifference
      .clone()
      .add(components.annualCarrierMismatch)
      .add(components.deferentBStage)
      .add(components.planeStage)
      .add(
        chainPosition(["Venus"], position).applyMatrix4(
          components.mainBasis
        )
      );
    const legacy = chainPosition(
      ["Venus deferent A", "Venus deferent B", "Venus Plane", "Venus"],
      position
    ).sub(chainPosition(["Sun deferent", "Sun"], position));
    maximumDifference = Math.max(
      maximumDifference,
      reconstructed.distanceTo(legacy)
    );
  }

  expect(maximumDifference).toBeLessThan(1e-10);
});

test("retains the complete non-zero Venus deferent-B translation", () => {
  const position = 4.25;
  const components = updateVenusSunRelativeComponents(
    createVenusSunRelativeComponents(),
    byName,
    position
  );
  const venusB = byName.get("Venus deferent B");

  expect(number(venusB, "orbitRadius")).toBeGreaterThan(0);
  expect(components.deferentBStage.length()).toBeCloseTo(
    number(venusB, "orbitRadius"),
    10
  );
});
