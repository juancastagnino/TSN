import { Quaternion, Spherical, Vector3 } from "three";
import { radToRa, radToDec } from "../utils/celestial-functions";
import { dateTimeToPos } from "./time-date-functions";

// Helper to convert degrees to radians
const D2R = Math.PI / 180;
const Y_AXIS = new Vector3(0, 1, 0);
const J2000_PLOT_POS = dateTimeToPos("2000-01-01", "12:00:00");

export const EPHEMERIS_REFERENCE_FRAMES = Object.freeze({
  TYCHOS_NATIVE: "tychos-native",
  J2000_ICRF: "j2000-icrf",
});

export const EPHEMERIS_REFERENCE_FRAME_OPTIONS = Object.freeze({
  "TYCHOS native (moving PVP)": EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE,
  "J2000 / ICRF comparison": EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF,
});

export function movePlotModel(plotObjects, plotPos) {
  plotObjects.forEach((pObj) => {
    if (pObj.orbitRef && pObj.orbitRef.current) {
      pObj.orbitRef.current.rotation.y =
        pObj.speed * plotPos - pObj.startPos * D2R;
    }
  });
}

/**
 * Return the orientation of Earth's equatorial frame at J2000 without moving
 * the live plot model. The current Earth-orbit rotation is removed from the
 * measured world quaternion and replaced with its value at J2000.
 *
 * The ancestors of Earth.orbitRef are static in the current model
 * (SystemCenter has zero speed). Keeping this calculation here makes the
 * reference-frame convention explicit and avoids using the star components as
 * an ephemeris reference.
 */
export function getJ2000EarthFrameQuaternion(plotObjects) {
  const earthObj = plotObjects.find((p) => p.name === "Earth");
  const orbit = earthObj?.orbitRef?.current;
  const cSphere = earthObj?.cSphereRef?.current;

  if (!earthObj || !orbit || !cSphere || !orbit.parent) return null;

  const orbitWorld = new Quaternion();
  const sphereWorld = new Quaternion();
  const orbitParentWorld = new Quaternion();

  orbit.getWorldQuaternion(orbitWorld);
  cSphere.getWorldQuaternion(sphereWorld);
  orbit.parent.getWorldQuaternion(orbitParentWorld);

  // Constant orientation from Earth.orbitRef down to Earth.cSphereRef.
  const orbitToSphere = orbitWorld.clone().invert().multiply(sphereWorld);
  const j2000OrbitAngle =
    Number(earthObj.speed) * J2000_PLOT_POS - Number(earthObj.startPos) * D2R;
  const j2000Orbit = new Quaternion().setFromAxisAngle(Y_AXIS, j2000OrbitAngle);

  return orbitParentWorld
    .multiply(j2000Orbit)
    .multiply(orbitToSphere)
    .normalize();
}

/**
 * Express a world-space target position in an Earth-centred reference frame.
 * Native mode deliberately preserves the historical TYCHOS calculation.
 * J2000 mode keeps Earth's current origin but uses a fixed J2000 orientation.
 */
export function getEarthFrameVector(
  targetPosition,
  earthObj,
  referenceFrame = EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE,
  j2000Quaternion = null
) {
  if (!earthObj?.pivotRef?.current || !earthObj?.cSphereRef?.current) {
    return null;
  }

  if (referenceFrame === EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE) {
    return earthObj.cSphereRef.current.worldToLocal(targetPosition.clone());
  }

  if (
    referenceFrame !== EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF ||
    !j2000Quaternion
  ) {
    return null;
  }

  const earthPosition = new Vector3();
  earthObj.pivotRef.current.getWorldPosition(earthPosition);

  return targetPosition
    .clone()
    .sub(earthPosition)
    .applyQuaternion(j2000Quaternion.clone().invert());
}

/** Convert an Earth-frame vector back to a world-space position for plotting. */
export function earthFrameVectorToWorld(
  earthFrameVector,
  earthObj,
  referenceFrame = EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE,
  j2000Quaternion = null
) {
  if (!earthObj?.pivotRef?.current || !earthObj?.cSphereRef?.current) {
    return null;
  }

  if (referenceFrame === EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE) {
    return earthObj.cSphereRef.current.localToWorld(earthFrameVector.clone());
  }

  if (
    referenceFrame !== EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF ||
    !j2000Quaternion
  ) {
    return null;
  }

  const earthPosition = new Vector3();
  earthObj.pivotRef.current.getWorldPosition(earthPosition);

  return earthFrameVector
    .clone()
    .applyQuaternion(j2000Quaternion)
    .add(earthPosition);
}

export function getPlotModelRaDecDistance(name, plotObjects, options = {}) {
  let targetName = name;
  if (name === "Moon") {
    const hasActualMoon = plotObjects.some((p) => p.name === "Actual Moon");
    if (hasActualMoon) targetName = "Actual Moon";
  }
  return getPlotRaDecDistanceFromPosition(targetName, plotObjects, options);
}

export function getPlotRaDecDistanceFromPosition(
  targetName,
  plotObjects,
  options = {}
) {
  const earthObj = plotObjects.find((p) => p.name === "Earth");
  const sunObj = plotObjects.find((p) => p.name === "Sun");
  const targetObj = plotObjects.find((p) => p.name === targetName);

  if (!earthObj || !sunObj || !targetObj) return null;

  // 1. Get World Positions
  const sunPos = new Vector3();
  const targetPos = new Vector3();

  if (sunObj.pivotRef?.current)
    sunObj.pivotRef.current.getWorldPosition(sunPos);
  if (targetObj.pivotRef?.current)
    targetObj.pivotRef.current.getWorldPosition(targetPos);

  const earthPos = new Vector3();
  if (earthObj.pivotRef?.current)
    earthObj.pivotRef.current.getWorldPosition(earthPos);

  // 2. Transform to the explicitly selected Earth-centred reference frame.
  const referenceFrame =
    options.referenceFrame || EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE;
  const j2000Quaternion =
    options.j2000Quaternion ||
    (referenceFrame === EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF
      ? getJ2000EarthFrameQuaternion(plotObjects)
      : null);
  const localVec = getEarthFrameVector(
    targetPos,
    earthObj,
    referenceFrame,
    j2000Quaternion
  );

  if (!localVec) return null;

  // 3. Convert Local Vector to Spherical Coordinates (RA/Dec)
  const sphericalPos = new Spherical().setFromVector3(localVec);

  const ra = radToRa(sphericalPos.theta);
  const dec = radToDec(sphericalPos.phi);

  // 4. Calculate Distances & Elongation
  const radius = sphericalPos.radius / 100;

  // Calculate distances for Elongation formula
  const earthSunDist = earthPos.distanceTo(sunPos);
  const sunTargetDist = sunPos.distanceTo(targetPos);
  const earthTargetDist = earthPos.distanceTo(targetPos); // Same as sphericalPos.radius

  // Cosine Rule for Elongation
  const numerator =
    earthSunDist * earthSunDist + // <--- FIXED: Typos corrected here
    earthTargetDist * earthTargetDist -
    sunTargetDist * sunTargetDist;

  const denominator = 2.0 * earthSunDist * earthTargetDist;

  // Clamp to [-1, 1] to prevent NaN from floating point errors
  const cosElong = Math.min(Math.max(numerator / denominator, -1), 1);
  const elongationRadians = Math.acos(cosElong);

  let elongation = ((180.0 * elongationRadians) / Math.PI).toFixed(3);
  elongation = isNaN(elongation) ? "-" : `${elongation}\u00B0`;

  let distanceDisplay = `${radius.toFixed(2)} AU`;
  if (radius < 0.01) {
    distanceDisplay = `${(radius * 149597871).toFixed(0)} km`;
  } else if (radius > 10000) {
    distanceDisplay = `${(radius * 0.0000158125).toFixed(3)} ly`;
  }

  return {
    ra,
    dec,
    elongation,
    dist: distanceDisplay,
  };
}
