import { Matrix4, Object3D, Vector3 } from "three";
import settings from "../settings/celestial-settings.json";
import { buildSettingsIndex, normalizeCelestialSettings } from "../utils/celestialSettingsSchema";
import {
  createSunMarsRelativeComponents,
  updateSunMarsRelativeComponents,
  updateSunRelativeFrame,
} from "./SunMarsRelativeOrbit";

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
  "reconstructs the legacy Sun-relative Mars vector at position %p",
  (position) => {
    const components = updateSunMarsRelativeComponents(
      createSunMarsRelativeComponents(),
      byName,
      position
    );
    const mars = byName.get("Mars");
    const localMarsRoot = chainPosition(["Mars"], position);
    const reconstructed = components.centreDifference
      .clone()
      .add(components.annualCarrierMismatch)
      .add(components.deferentSHarmonic)
      .add(localMarsRoot.applyMatrix4(components.mainBasis));
    const legacy = chainPosition(
      ["Mars deferent E", "Mars deferent S", "Mars"],
      position
    ).sub(chainPosition(["Sun deferent", "Sun"], position));

    expect(mars.orbitRadius).toBeGreaterThan(0);
    expect(reconstructed.distanceTo(legacy)).toBeLessThan(1e-10);
  }
);

test("places the relative frame at the Sun while retaining binary-frame axes", () => {
  const worldRoot = new Object3D();
  worldRoot.position.set(7, -4, 2);
  worldRoot.rotation.set(0.1, -0.2, 0.05);

  const binaryFrame = new Object3D();
  binaryFrame.name = "Sun-Mars Binary Frame";
  binaryFrame.position.set(3, 1, -2);
  binaryFrame.rotation.set(-0.04, 0.3, 0.02);
  worldRoot.add(binaryFrame);

  const sunParent = new Object3D();
  sunParent.position.set(100, -0.5, 3.3);
  sunParent.rotation.set(0.01, 1.2, -0.02);
  binaryFrame.add(sunParent);

  const relativeFrame = new Object3D();
  relativeFrame.matrixAutoUpdate = false;
  sunParent.add(relativeFrame);
  const marker = new Object3D();
  marker.position.set(2, 0, 0);
  relativeFrame.add(marker);

  expect(updateSunRelativeFrame(relativeFrame)).toBe(true);
  worldRoot.updateMatrixWorld(true);

  const actualOrigin = relativeFrame.getWorldPosition(new Vector3());
  const expectedOrigin = sunParent.getWorldPosition(new Vector3());
  expect(actualOrigin.distanceTo(expectedOrigin)).toBeLessThan(1e-10);

  const actualMarker = marker.getWorldPosition(new Vector3());
  const expectedMarker = new Vector3(2, 0, 0)
    .applyMatrix4(new Matrix4().extractRotation(binaryFrame.matrixWorld))
    .add(expectedOrigin);
  expect(actualMarker.distanceTo(expectedMarker)).toBeLessThan(1e-10);
});
