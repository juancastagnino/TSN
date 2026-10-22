import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Quaternion, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { findCelestialSetting } from "../utils/celestialSettingsSchema";

const D2R = Math.PI / 180;
const DISPLAY_MOON_SCALE = 39.2078;
export const MOON_SOLAR_ECCENTRIC_UPDATER =
  "Moon Solar-Coupled Eccentric Updater";

const finite = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

export const wrapRadians = (value) =>
  Math.atan2(Math.sin(value), Math.cos(value));

// THREE.RotationY(angle) maps +X toward -Z, hence atan2(-z, x).
export const signedAngleInEclipticXZ = (vector) =>
  Math.atan2(-vector.z, vector.x);

export const deriveSolarCoupledLunarAngles = (
  earthToMoonEcliptic,
  earthToSunEcliptic,
  anomalisticPhase
) => {
  const moonLongitude = signedAngleInEclipticXZ(earthToMoonEcliptic);
  const sunLongitude = signedAngleInEclipticXZ(earthToSunEcliptic);
  const elongation = wrapRadians(moonLongitude - sunLongitude);
  const inequalityArgument = wrapRadians(2 * elongation - anomalisticPhase);
  const variationArgument = wrapRadians(2 * elongation);

  // 2D-M is the wanted longitude-correction argument, not the absolute
  // direction of the eccentric centre. A small centre displacement changes
  // observed lunar longitude according to its angle relative to the Moon.
  const eccentricOrientation = wrapRadians(
    moonLongitude + inequalityArgument
  );
  const variationOrientation = wrapRadians(
    moonLongitude + variationArgument
  );
  return {
    moonLongitude,
    sunLongitude,
    elongation,
    anomalisticPhase,
    inequalityArgument,
    eccentricOrientation,
    variationArgument,
    variationOrientation,
  };
};

export const scaleRadialProjection = (
  displacement,
  radialDirection,
  radialMultiplier,
  target = new Vector3()
) => {
  const radialLengthSq = radialDirection.lengthSq();
  if (radialLengthSq === 0) return target.copy(displacement);
  const radialScale = displacement.dot(radialDirection) / radialLengthSq;
  return target
    .copy(displacement)
    .addScaledVector(
      radialDirection,
      radialScale * (radialMultiplier - 1)
    );
};

export const composeSolarCoupledLunarOffset = (
  angles,
  radialDirection,
  inequalityAmplitude,
  variationAmplitude,
  target = new Vector3(),
  variation = new Vector3()
) => {
  target.set(
    Math.cos(angles.eccentricOrientation) * inequalityAmplitude,
    0,
    -Math.sin(angles.eccentricOrientation) * inequalityAmplitude
  );
  scaleRadialProjection(target, radialDirection, -1, target);

  variation.set(
    Math.cos(angles.variationOrientation) * variationAmplitude,
    0,
    -Math.sin(angles.variationOrientation) * variationAmplitude
  );
  scaleRadialProjection(variation, radialDirection, -1, variation);
  return target.add(variation);
};

// Python experiment: two equal world-XZ vectors at apsis and 2*Moon-apsis.
// Their sum is radial only in the XZ projection, not necessarily in 3D.
export const composePairedRadialOffset = (moonDirection, apsidalAxis, radius, target = new Vector3()) => {
  const moonAngle = signedAngleInEclipticXZ(moonDirection);
  const apsidalAngle = signedAngleInEclipticXZ(apsidalAxis);
  const secondAngle = 2 * moonAngle - apsidalAngle;
  return target.set(
    radius * (Math.cos(apsidalAngle) + Math.cos(secondAngle)),
    0,
    -radius * (Math.sin(apsidalAngle) + Math.sin(secondAngle))
  );
};

const MoonSolarCoupledEccentric = ({
  children,
  targetName = "Moon",
  plotMode = false,
}) => {
  const { scene } = useThree();
  const setting = useSettingsStore(
    useCallback(
      (state) =>
        findCelestialSetting(state.settings, "moon-solar-eccentric"),
      []
    )
  );
  const moon = useSettingsStore(
    useCallback(
      (state) => findCelestialSetting(state.settings, "moon"),
      []
    )
  );
  const pairedRadial = useSettingsStore(
    useCallback((state) => findCelestialSetting(state.settings, "moon-paired-radial"), [])
  );
  const actualPlanetSizes = useStore((state) => state.actualPlanetSizes);
  const posRef = useStore((state) => state.posRef);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);

  const offsetRef = useRef();
  const earthWorld = useMemo(() => new Vector3(), []);
  const sunWorld = useMemo(() => new Vector3(), []);
  const moonWorld = useMemo(() => new Vector3(), []);
  const earthToMoonEcliptic = useMemo(() => new Vector3(), []);
  const earthToSunEcliptic = useMemo(() => new Vector3(), []);
  const parentQuaternionInverse = useMemo(() => new Quaternion(), []);
  const localOffset = useMemo(() => new Vector3(), []);
  const eccentricWorld = useMemo(() => new Vector3(), []);
  const variationWorld = useMemo(() => new Vector3(), []);
  const apsidalAxisWorld = useMemo(() => new Vector3(), []);
  const pairedWorld = useMemo(() => new Vector3(), []);
  const parentQuaternion = useMemo(() => new Quaternion(), []);

  const physicalCoordinates = targetName.startsWith("Actual ");
  const distanceScale =
    actualPlanetSizes || physicalCoordinates ? 1 : DISPLAY_MOON_SCALE;
  const inequalityAmplitude = finite(setting?.orbitRadius) * distanceScale;
  const variationAmplitude =
    finite(setting?.solarVariationRadius) * distanceScale;
  const pairedRadius = finite(pairedRadial?.orbitRadius) * distanceScale;
  const updaterName = `${MOON_SOLAR_ECCENTRIC_UPDATER}:${targetName}`;

  const update = useCallback(
    (position) => {
      const offset = offsetRef.current;
      const parent = offset?.parent;
      if (!offset || !parent || !moon) return false;

      const plotObjects = usePlotStore.getState().plotObjects;
      const earthObject = plotMode
        ? plotObjects.find((item) => item.name === "Earth")?.pivotRef?.current
        : scene.getObjectByName("Earth");
      const sunObject = plotMode
        ? plotObjects.find((item) => item.name === "Sun")?.pivotRef?.current
        : scene.getObjectByName("Sun");
      const moonObject = plotMode
        ? plotObjects.find((item) => item.name === targetName)?.pivotRef?.current
        : scene.getObjectByName(targetName);
      if (!earthObject || !sunObject || !moonObject) return false;

      const modelPosition = Number.isFinite(position) ? position : 0;
      const anomalisticPhase =
        finite(moon.speed) * modelPosition - finite(moon.startPos) * D2R;

      // Sample the accepted geometry without feeding the experimental offset
      // back into its own angle calculation.
      offset.position.set(0, 0, 0);
      parent.updateWorldMatrix(true, true);
      earthObject.getWorldPosition(earthWorld);
      sunObject.getWorldPosition(sunWorld);
      moonObject.getWorldPosition(moonWorld);

      // World XZ is the model's fixed ecliptic reference. Both directions are
      // measured here before the centre vector is converted into the moving
      // Moon-stage parent's local coordinates.
      earthToMoonEcliptic.subVectors(moonWorld, earthWorld);
      earthToSunEcliptic.subVectors(sunWorld, earthWorld);
      if (
        earthToMoonEcliptic.lengthSq() === 0 ||
        earthToSunEcliptic.lengthSq() === 0
      ) {
        return false;
      }

      const angles = deriveSolarCoupledLunarAngles(
        earthToMoonEcliptic,
        earthToSunEcliptic,
        anomalisticPhase
      );
      parent.getWorldQuaternion(parentQuaternion);
      parentQuaternionInverse.copy(parentQuaternion).invert();
      // Both contributions remain translations of one solar-coupled lunar
      // centre. The first follows 2D-M; the second follows the independently
      // identified 2D geometry. Reflecting their radial projections preserves
      // the tested angular sense without introducing a post-export correction.
      composeSolarCoupledLunarOffset(
        angles,
        earthToMoonEcliptic,
        inequalityAmplitude,
        variationAmplitude,
        eccentricWorld,
        variationWorld
      );
      apsidalAxisWorld.set(1, 0, 0).applyQuaternion(parentQuaternion);
      composePairedRadialOffset(earthToMoonEcliptic, apsidalAxisWorld, pairedRadius, pairedWorld);
      eccentricWorld.add(pairedWorld);
      localOffset
        .copy(eccentricWorld)
        .applyQuaternion(parentQuaternionInverse);
      offset.position.copy(localOffset);
      offset.updateWorldMatrix(true, true);
      return true;
    },
    [
      eccentricWorld,
      apsidalAxisWorld,
      earthToMoonEcliptic,
      earthToSunEcliptic,
      earthWorld,
      inequalityAmplitude,
      localOffset,
      moon,
      moonWorld,
      parentQuaternionInverse,
      parentQuaternion,
      pairedRadius,
      pairedWorld,
      plotMode,
      scene,
      sunWorld,
      targetName,
      variationAmplitude,
      variationWorld,
    ]
  );

  useFrame(() => update(posRef.current));

  useEffect(() => {
    if (!plotMode) return undefined;
    addPlotObj({ name: updaterName, updateAfterMotion: update });
    return () => removePlotObj(updaterName);
  }, [addPlotObj, plotMode, removePlotObj, update, updaterName]);

  if (
    !setting ||
    !moon
  ) {
    return null;
  }

  return (
    <group ref={offsetRef} name={`${targetName} Solar-Coupled Eccentric Offset`}>
      {children}
    </group>
  );
};

export default MoonSolarCoupledEccentric;
