import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";

export const SUN_MARS_FRAME_NAME = "Sun-Mars Binary Frame";
export const SUN_MARS_RELATIVE_UPDATER_NAME = "Sun-Mars Relative Components";

const D2R = Math.PI / 180;

const number = (setting, key) => Number(setting?.[key] || 0);

const settingCenter = (setting, target) =>
  target.set(
    number(setting, "orbitCentera"),
    number(setting, "orbitCenterc"),
    number(setting, "orbitCenterb")
  );

const orbitalOrientation = (setting, position, target, scratch) => {
  target.makeRotationX(number(setting, "orbitTilta") * D2R);
  scratch.makeRotationZ(number(setting, "orbitTiltb") * D2R);
  target.multiply(scratch);
  scratch.makeRotationY(
    number(setting, "speed") * position -
      number(setting, "startPos") * D2R
  );
  target.multiply(scratch);
  return target;
};

export const createSunMarsRelativeComponents = () => ({
  centreDifference: new Vector3(),
  annualCarrierMismatch: new Vector3(),
  deferentSHarmonic: new Vector3(),
  mainBasis: new Matrix4(),
  eOrientation: new Matrix4(),
  sOrientation: new Matrix4(),
  sunOrientation: new Matrix4(),
  scratchMatrix: new Matrix4(),
  scratchVectorA: new Vector3(),
});

/**
 * Expand the accepted Mars/Sun settings into the four Phase 3D components.
 * Vectors are expressed in the common Earth/PVP-carried binary frame.
 */
export const updateSunMarsRelativeComponents = (
  target,
  settingsByName,
  position
) => {
  const get = (name) =>
    settingsByName instanceof Map
      ? settingsByName.get(name)
      : settingsByName[name];
  const sun = get("Sun");
  const marsE = get("Mars deferent E");
  const marsS = get("Mars deferent S");

  orbitalOrientation(
    marsE,
    position,
    target.eOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    marsS,
    position,
    target.sOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    sun,
    position,
    target.sunOrientation,
    target.scratchMatrix
  );

  settingCenter(marsE, target.centreDifference);
  settingCenter(sun, target.scratchVectorA);
  target.centreDifference.sub(target.scratchVectorA);

  target.annualCarrierMismatch
    .set(number(marsE, "orbitRadius"), 0, 0)
    .applyMatrix4(target.eOrientation);
  target.scratchVectorA
    .set(number(sun, "orbitRadius"), 0, 0)
    .applyMatrix4(target.sunOrientation);
  target.annualCarrierMismatch.sub(target.scratchVectorA);

  target.deferentSHarmonic
    .set(number(marsS, "orbitRadius"), 0, 0)
    .applyMatrix4(target.sOrientation);
  settingCenter(marsS, target.scratchVectorA);
  target.deferentSHarmonic
    .add(target.scratchVectorA)
    .applyMatrix4(target.eOrientation);

  target.mainBasis.multiplyMatrices(
    target.eOrientation,
    target.sOrientation
  );
  return target;
};

/** Place a local frame at the Sun while retaining the binary frame's axes. */
export const updateSunRelativeFrame = (
  root,
  frameName = SUN_MARS_FRAME_NAME,
  inverseParent = new Matrix4(),
  desiredWorld = new Matrix4(),
  sunWorld = new Vector3()
) => {
  const parent = root?.parent;
  if (!parent) return false;

  let frame = parent;
  while (frame && frame.name !== frameName) frame = frame.parent;
  if (!frame) return false;

  parent.updateWorldMatrix(true, false);
  frame.updateWorldMatrix(true, false);
  parent.getWorldPosition(sunWorld);
  desiredWorld.copy(frame.matrixWorld).setPosition(sunWorld);
  inverseParent.copy(parent.matrixWorld).invert();
  root.matrix.multiplyMatrices(inverseParent, desiredWorld);
  root.matrixWorldNeedsUpdate = true;
  return true;
};

/**
 * Exact Phase 3E re-expression of the legacy Mars deferent-E/deferent-S prefix.
 * The leaf Mars object still supplies its own configured centre, tilt, phase and
 * radius, so Phobos and Deimos inherit the same final orientation as before.
 */
const SunMarsRelativeOrbit = ({ children, plotMode = false }) => {
  const settings = useSettingsStore((state) => state.settings);
  const settingsByName = useMemo(
    () => new Map(settings.map((setting) => [setting.name, setting])),
    [settings]
  );
  const components = useMemo(createSunMarsRelativeComponents, []);
  const rootRef = useRef();
  const centreRef = useRef();
  const carrierRef = useRef();
  const harmonicRef = useRef();
  const mainBasisRef = useRef();
  const inverseParent = useMemo(() => new Matrix4(), []);
  const desiredWorld = useMemo(() => new Matrix4(), []);
  const sunWorld = useMemo(() => new Vector3(), []);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);
  const posRef = useStore((state) => state.posRef);

  const update = useCallback(
    (position) => {
      const modelPosition = Number.isFinite(position) ? position : 0;
      updateSunMarsRelativeComponents(
        components,
        settingsByName,
        modelPosition
      );
      centreRef.current?.position.copy(components.centreDifference);
      carrierRef.current?.position.copy(components.annualCarrierMismatch);
      harmonicRef.current?.position.copy(components.deferentSHarmonic);
      mainBasisRef.current?.quaternion.setFromRotationMatrix(
        components.mainBasis
      );
      return updateSunRelativeFrame(
        rootRef.current,
        SUN_MARS_FRAME_NAME,
        inverseParent,
        desiredWorld,
        sunWorld
      );
    },
    [components, desiredWorld, inverseParent, settingsByName, sunWorld]
  );

  useFrame(() => update(posRef.current));

  useEffect(() => {
    if (!plotMode) return undefined;
    addPlotObj({
      name: SUN_MARS_RELATIVE_UPDATER_NAME,
      updateAfterMotion: update,
    });
    return () => removePlotObj(SUN_MARS_RELATIVE_UPDATER_NAME);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  return (
    <group
      ref={rootRef}
      name="Sun-Relative Mars Frame"
      matrixAutoUpdate={false}
    >
      <group ref={centreRef} name="Sun-Mars Centre Difference">
        <group ref={carrierRef} name="Sun-Mars Annual Carrier Mismatch">
          <group ref={harmonicRef} name="Mars Deferent-S Harmonic">
            <group ref={mainBasisRef} name="Mars Main-Orbit Basis">
              {children}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default SunMarsRelativeOrbit;
