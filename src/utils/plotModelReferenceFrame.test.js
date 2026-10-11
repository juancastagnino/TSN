import { Object3D, Vector3 } from "three";
import { dateTimeToPos } from "./time-date-functions";
import {
  EPHEMERIS_REFERENCE_FRAMES,
  getEarthFrameVector,
  getJ2000EarthFrameQuaternion,
} from "./plotModelFunctions";

const EARTH_SPEED = -0.0002479160869310127;

function makeEarth() {
  const root = new Object3D();
  const orbit = new Object3D();
  const pivot = new Object3D();
  const sphere = new Object3D();
  root.add(orbit);
  orbit.add(pivot);
  pivot.add(sphere);
  sphere.rotation.set(
    0.26 * (Math.PI / 180),
    0,
    -23.439062 * (Math.PI / 180)
  );
  return {
    root,
    orbit,
    earth: {
      name: "Earth",
      speed: EARTH_SPEED,
      startPos: 0,
      orbitRef: { current: orbit },
      pivotRef: { current: pivot },
      cSphereRef: { current: sphere },
    },
  };
}

test("fixed J2000 orientation is independent of the current Earth angle", () => {
  const { root, orbit, earth } = makeEarth();
  orbit.rotation.y = 0.4;
  root.updateMatrixWorld(true);
  const first = getJ2000EarthFrameQuaternion([earth]);
  orbit.rotation.y = -0.8;
  root.updateMatrixWorld(true);
  const second = getJ2000EarthFrameQuaternion([earth]);
  expect(first.angleTo(second)).toBeLessThan(1e-10);
});

test("native and fixed frames coincide at the J2000 epoch", () => {
  const { root, orbit, earth } = makeEarth();
  orbit.rotation.y =
    EARTH_SPEED * dateTimeToPos("2000-01-01", "12:00:00");
  root.updateMatrixWorld(true);
  const target = new Vector3(8, 3, -5);
  const fixed = getJ2000EarthFrameQuaternion([earth]);
  const nativeVector = getEarthFrameVector(target, earth);
  const fixedVector = getEarthFrameVector(
    target,
    earth,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    fixed
  );
  expect(nativeVector.distanceTo(fixedVector)).toBeLessThan(1e-10);
});

test("fixed-frame conversion preserves vector length", () => {
  const { root, earth } = makeEarth();
  root.updateMatrixWorld(true);
  const target = new Vector3(8, 3, -5);
  const fixed = getJ2000EarthFrameQuaternion([earth]);
  const converted = getEarthFrameVector(
    target,
    earth,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    fixed
  );
  expect(converted.length()).toBeCloseTo(target.length(), 10);
});
