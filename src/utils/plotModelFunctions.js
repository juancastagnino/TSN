import { Vector3, Spherical } from "three";
import {
  latToRad,
  longToRad,
  radToRa,
  radToDec,
} from "../utils/celestial-functions";
import {
  createSunMarsBinaryDiagnostics,
  createSunMarsBinaryState,
  createSunMarsPrimaryCompanionState,
  updateSunMarsBinaryDiagnostics,
  updateSunMarsBinaryState,
  updateSunMarsPrimaryCompanionState,
} from "./sunMarsBinaryState";

// Helper to convert degrees to radians
const D2R = Math.PI / 180;
const plotBinaryState = createSunMarsBinaryState();

export function movePlotModel(plotObjects, plotPos) {
  plotObjects.forEach((pObj) => {
    if (pObj.orbitRef && pObj.orbitRef.current) {
      pObj.orbitRef.current.rotation.y =
        pObj.speed * plotPos - pObj.startPos * D2R;
    }
  });

  // Coordinate adapters depend on the final orbital rotations for this sample.
  // Negative-priority geometry must settle before dependent adapters.
  plotObjects.forEach((pObj) => {
    if (pObj.updatePriority < 0) pObj.updateAfterMotion?.(plotPos);
  });
  plotObjects.forEach((pObj) => {
    if (!(pObj.updatePriority < 0)) pObj.updateAfterMotion?.(plotPos);
  });

  return getPlotSunMarsBinaryState(plotObjects, plotBinaryState);
}

/**
 * Derive the same common-centre companion vectors from the hidden plot model.
 * Callers may pass a reusable target when sampling many ephemeris positions.
 */
export function getPlotSunMarsBinaryState(
  plotObjects,
  target = createSunMarsBinaryState()
) {
  const earthObj = plotObjects.find((p) => p.name === "Earth");
  const sunObj = plotObjects.find((p) => p.name === "Sun");
  const marsObj = plotObjects.find((p) => p.name === "Mars");

  const earthPivot = earthObj?.pivotRef?.current;
  const sunPivot = sunObj?.pivotRef?.current;
  const marsPivot = marsObj?.pivotRef?.current;
  if (!earthPivot || !sunPivot || !marsPivot) {
    target.valid = false;
    return target;
  }

  earthPivot.getWorldPosition(target.centerWorld);
  sunPivot.getWorldPosition(target.sunWorld);
  marsPivot.getWorldPosition(target.marsWorld);
  return updateSunMarsBinaryState(
    target,
    target.centerWorld,
    target.sunWorld,
    target.marsWorld
  );
}

export function getPlotSunMarsBinaryDiagnostics(
  plotObjects,
  target = createSunMarsBinaryDiagnostics()
) {
  const systemCenterObj = plotObjects.find((p) => p.name === "SystemCenter");
  const earthObj = plotObjects.find((p) => p.name === "Earth");
  const sunObj = plotObjects.find((p) => p.name === "Sun");
  const marsObj = plotObjects.find((p) => p.name === "Mars");

  const systemCenterPivot = systemCenterObj?.pivotRef?.current;
  const earthPivot = earthObj?.pivotRef?.current;
  const sunPivot = sunObj?.pivotRef?.current;
  const marsPivot = marsObj?.pivotRef?.current;
  const marsOrbit = marsObj?.orbitRef?.current;
  const earthEquatorial = earthObj?.cSphereRef?.current;
  if (
    !systemCenterPivot ||
    !earthPivot ||
    !sunPivot ||
    !marsPivot ||
    !marsOrbit ||
    !earthEquatorial
  ) {
    target.valid = false;
    return target;
  }

  systemCenterPivot.getWorldPosition(target.sample.pvpWorld);
  earthPivot.getWorldPosition(target.sample.earthWorld);
  sunPivot.getWorldPosition(target.sample.sunWorld);
  marsPivot.getWorldPosition(target.sample.marsWorld);
  marsOrbit.getWorldQuaternion(target.sample.marsOrbitQuaternion);
  target.sample.marsOrbitNormalWorld
    .set(0, 1, 0)
    .applyQuaternion(target.sample.marsOrbitQuaternion)
    .normalize();
  earthEquatorial.getWorldQuaternion(target.sample.earthEquatorialQuaternion);
  target.sample.earthEquatorialAxisX
    .set(1, 0, 0)
    .applyQuaternion(target.sample.earthEquatorialQuaternion);
  target.sample.earthEquatorialAxisY
    .set(0, 1, 0)
    .applyQuaternion(target.sample.earthEquatorialQuaternion);
  target.sample.earthEquatorialAxisZ
    .set(0, 0, 1)
    .applyQuaternion(target.sample.earthEquatorialQuaternion);
  return updateSunMarsBinaryDiagnostics(
    target,
    target.sample.earthWorld,
    target.sample.pvpWorld,
    target.sample.sunWorld,
    target.sample.marsWorld
  );
}

/**
 * Express the hidden model's existing Mars position relative to the Sun.
 * No transform is changed and world-space reconstruction remains exact.
 */
export function getPlotSunMarsPrimaryCompanionState(
  plotObjects,
  target = createSunMarsPrimaryCompanionState()
) {
  const sunObj = plotObjects.find((p) => p.name === "Sun");
  const marsObj = plotObjects.find((p) => p.name === "Mars");
  const sunPivot = sunObj?.pivotRef?.current;
  const marsPivot = marsObj?.pivotRef?.current;
  if (!sunPivot || !marsPivot) {
    target.valid = false;
    return target;
  }

  sunPivot.getWorldPosition(target.primaryWorld);
  marsPivot.getWorldPosition(target.companionWorld);
  return updateSunMarsPrimaryCompanionState(
    target,
    target.primaryWorld,
    target.companionWorld
  );
}

export function getPlotModelRaDecDistance(name, plotObjects, observer = null) {
  let targetName = name;
  if (name === "Moon") {
    const hasActualMoon = plotObjects.some((p) => p.name === "Actual Moon");
    if (hasActualMoon) targetName = "Actual Moon";
  }
  return getPlotRaDecDistanceFromPosition(targetName, plotObjects, observer);
}

export function getPlotRaDecDistanceFromPosition(
  targetName,
  plotObjects,
  observer = null
) {
  const earthObj = plotObjects.find((p) => p.name === "Earth");
  const sunObj = plotObjects.find((p) => p.name === "Sun");
  const targetObj = plotObjects.find((p) => p.name === targetName);

  if (!earthObj || !sunObj || !targetObj) return null;

  // 1. Get World Positions
  const sunPos = new Vector3();
  const targetPos = new Vector3();
  
  if (sunObj.pivotRef?.current) sunObj.pivotRef.current.getWorldPosition(sunPos);
  if (targetObj.pivotRef?.current) targetObj.pivotRef.current.getWorldPosition(targetPos);
  
  const earthPos = new Vector3();
  if (earthObj.pivotRef?.current) earthObj.pivotRef.current.getWorldPosition(earthPos);

  // 2. TRANSFORM TO EARTH EQUATORIAL FRAME
  // We convert the target's World Position into the local space of Earth's tilted sphere (cSphereRef).
  // This automatically accounts for Earth's axial tilt without manual quaternion math.
  
  const localVec = targetPos.clone();
  const observerWorld = new Vector3();
  let isTopocentric = false;
  
  if (earthObj.cSphereRef?.current) {
    // Transforms from World Space -> Tilted Earth Space (Equatorial)
    const earthFrame = earthObj.cSphereRef.current;
    earthFrame.worldToLocal(localVec);

    if (observer?.radius && Number.isFinite(observer.time)) {
      const observerLocal = new Vector3(0, Number(observer.radius), 0)
        .applyAxisAngle(new Vector3(1, 0, 0), latToRad(observer.latitude))
        .applyAxisAngle(new Vector3(0, 1, 0), longToRad(observer.longitude))
        .applyAxisAngle(
          new Vector3(0, 1, 0),
          Number(observer.rotationStart || 0) +
            Number(observer.rotationSpeed || 0) * Number(observer.time)
        );
      localVec.sub(observerLocal);
      observerWorld.copy(observerLocal);
      earthFrame.localToWorld(observerWorld);
      isTopocentric = true;
    }
  }

  // 3. Convert Local Vector to Spherical Coordinates (RA/Dec)
  const sphericalPos = new Spherical().setFromVector3(localVec);

  const ra = radToRa(sphericalPos.theta);
  const dec = radToDec(sphericalPos.phi);

  // 4. Calculate Distances & Elongation
  const radius = sphericalPos.radius / 100;
  
  // Calculate distances for Elongation formula
  const sunTargetDist = sunPos.distanceTo(targetPos);
  const observationOrigin = isTopocentric ? observerWorld : earthPos;
  const earthSunDist = observationOrigin.distanceTo(sunPos);
  const earthTargetDist = observationOrigin.distanceTo(targetPos);

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
