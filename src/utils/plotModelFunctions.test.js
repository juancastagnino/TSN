import { Object3D, Vector3 } from "three";
import { dateTimeToPos } from "./time-date-functions";
import {
  EPHEMERIS_REFERENCE_FRAMES,
  earthFrameVectorToWorld,
  getEarthFrameVector,
  getJ2000EarthFrameQuaternion,
} from "./plotModelFunctions";

const EARTH_SPEED = -0.0002479160869310127;

function makeEarthHierarchy(pivotPosition = new Vector3()) {
  const root = new Object3D();
  const container = new Object3D();
  const orbit = new Object3D();
  const pivot = new Object3D();
  const cSphere = new Object3D();

  root.add(container);
  container.add(orbit);
  orbit.add(pivot);
  pivot.add(cSphere);

  pivot.position.copy(pivotPosition);
  cSphere.rotation.set(0.26 * (Math.PI / 180), 0, -23.439062 * (Math.PI / 180));

  const earthObj = {
    name: "Earth",
    speed: EARTH_SPEED,
    startPos: 0,
    orbitRef: { current: orbit },
    pivotRef: { current: pivot },
    cSphereRef: { current: cSphere },
  };

  return { root, orbit, pivot, cSphere, earthObj };
}

function expectVectorClose(actual, expected, tolerance = 1e-10) {
  expect(actual.distanceTo(expected)).toBeLessThan(tolerance);
}

test("native frame preserves the historical cSphere.worldToLocal calculation", () => {
  const { root, orbit, cSphere, earthObj } = makeEarthHierarchy(
    new Vector3(2, 0, 0)
  );
  const target = new Object3D();
  target.position.set(8, 3, -5);
  root.add(target);

  orbit.rotation.y = 0.7;
  root.updateMatrixWorld(true);

  const targetWorld = target.getWorldPosition(new Vector3());
  const expected = cSphere.worldToLocal(targetWorld.clone());
  const actual = getEarthFrameVector(targetWorld, earthObj);

  expectVectorClose(actual, expected);
});

test("J2000 frame quaternion does not depend on the current Earth orbit angle", () => {
  const { root, orbit, earthObj } = makeEarthHierarchy();
  const plotObjects = [earthObj];

  orbit.rotation.y = 0.2;
  root.updateMatrixWorld(true);
  const first = getJ2000EarthFrameQuaternion(plotObjects);

  orbit.rotation.y = -0.9;
  root.updateMatrixWorld(true);
  const second = getJ2000EarthFrameQuaternion(plotObjects);

  expect(first.angleTo(second)).toBeLessThan(1e-10);
});

test("native and J2000 frames coincide at the J2000 reference epoch", () => {
  const { root, orbit, earthObj } = makeEarthHierarchy(new Vector3(2, 0, 0));
  const target = new Object3D();
  target.position.set(8, 3, -5);
  root.add(target);

  const j2000Pos = dateTimeToPos("2000-01-01", "12:00:00");
  orbit.rotation.y = EARTH_SPEED * j2000Pos;
  root.updateMatrixWorld(true);

  const plotObjects = [earthObj];
  const j2000Quaternion = getJ2000EarthFrameQuaternion(plotObjects);
  const targetWorld = target.getWorldPosition(new Vector3());
  const nativeVector = getEarthFrameVector(targetWorld, earthObj);
  const j2000Vector = getEarthFrameVector(
    targetWorld,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );

  expectVectorClose(j2000Vector, nativeVector);
});

test("a fixed world direction remains fixed in the J2000 frame", () => {
  const { root, orbit, earthObj } = makeEarthHierarchy();
  const target = new Object3D();
  target.position.set(8, 3, -5);
  root.add(target);

  root.updateMatrixWorld(true);
  const j2000Quaternion = getJ2000EarthFrameQuaternion([earthObj]);
  const targetWorld = target.getWorldPosition(new Vector3());

  orbit.rotation.y = 0.25;
  root.updateMatrixWorld(true);
  const first = getEarthFrameVector(
    targetWorld,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );

  orbit.rotation.y = -0.75;
  root.updateMatrixWorld(true);
  const second = getEarthFrameVector(
    targetWorld,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );

  expectVectorClose(first, second);
});

test("J2000 orientation preserves distances and angular separations", () => {
  const { root, earthObj } = makeEarthHierarchy();
  root.updateMatrixWorld(true);
  const j2000Quaternion = getJ2000EarthFrameQuaternion([earthObj]);
  const firstWorld = new Vector3(8, 3, -5);
  const secondWorld = new Vector3(-2, 7, 4);

  const first = getEarthFrameVector(
    firstWorld,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );
  const second = getEarthFrameVector(
    secondWorld,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );

  expect(first.length()).toBeCloseTo(firstWorld.length(), 10);
  expect(second.length()).toBeCloseTo(secondWorld.length(), 10);
  expect(first.angleTo(second)).toBeCloseTo(
    firstWorld.angleTo(secondWorld),
    10
  );
});

test("J2000 Earth-frame conversion round-trips a world position", () => {
  const { root, earthObj } = makeEarthHierarchy(new Vector3(2, 0, 0));
  root.updateMatrixWorld(true);
  const j2000Quaternion = getJ2000EarthFrameQuaternion([earthObj]);
  const worldPosition = new Vector3(8, 3, -5);

  const earthFramePosition = getEarthFrameVector(
    worldPosition,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );
  const reconstructed = earthFrameVectorToWorld(
    earthFramePosition,
    earthObj,
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
    j2000Quaternion
  );

  expectVectorClose(reconstructed, worldPosition);
});
