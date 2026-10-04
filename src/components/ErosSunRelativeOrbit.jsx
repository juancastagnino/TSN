import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import {
  SUN_MARS_FRAME_NAME,
  updateSunRelativeFrame,
} from "./SunMarsRelativeOrbit";

export const EROS_SUN_RELATIVE_UPDATER_NAME = "Eros Sun-Relative Components";

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

export const createErosSunRelativeComponents = () => ({
  centreDifference: new Vector3(),
  annualCarrierMismatch: new Vector3(),
  deferentBStage: new Vector3(),
  mainBasis: new Matrix4(),
  aOrientation: new Matrix4(),
  bOrientation: new Matrix4(),
  sunDeferentOrientation: new Matrix4(),
  sunOrientation: new Matrix4(),
  scratchMatrix: new Matrix4(),
  scratchVector: new Vector3(),
});

/**
 * Expand the legacy Eros A -> B prefix into the exact Phase 4D components.
 * The unchanged Eros leaf supplies its centre, phase and radius beneath the
 * reconstructed A*B main basis.
 */
export const updateErosSunRelativeComponents = (
  target,
  settingsByName,
  position
) => {
  const get = (name) =>
    settingsByName instanceof Map
      ? settingsByName.get(name)
      : settingsByName[name];
  const sunDeferent = get("Sun deferent");
  const sun = get("Sun");
  const erosA = get("Eros deferent A");
  const erosB = get("Eros deferent B");

  orbitalOrientation(
    erosA,
    position,
    target.aOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    erosB,
    position,
    target.bOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    sunDeferent,
    position,
    target.sunDeferentOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    sun,
    position,
    target.sunOrientation,
    target.scratchMatrix
  );

  // cA - cSunDeferent - QSunDeferent*cSun
  settingCenter(erosA, target.centreDifference);
  settingCenter(sunDeferent, target.scratchVector);
  target.centreDifference.sub(target.scratchVector);
  settingCenter(sun, target.scratchVector).applyMatrix4(
    target.sunDeferentOrientation
  );
  target.centreDifference.sub(target.scratchVector);

  // QA*rA - QD*rD - QD*QSun*rSun. The two radius-100 carriers
  // have different tilts, so this remainder is intentionally non-zero.
  target.annualCarrierMismatch
    .set(number(erosA, "orbitRadius"), 0, 0)
    .applyMatrix4(target.aOrientation);
  target.scratchVector
    .set(number(sunDeferent, "orbitRadius"), 0, 0)
    .applyMatrix4(target.sunDeferentOrientation);
  target.annualCarrierMismatch.sub(target.scratchVector);
  target.scratchVector
    .set(number(sun, "orbitRadius"), 0, 0)
    .applyMatrix4(target.sunOrientation)
    .applyMatrix4(target.sunDeferentOrientation);
  target.annualCarrierMismatch.sub(target.scratchVector);

  // QA*(cB + QB*rB)
  target.deferentBStage
    .set(number(erosB, "orbitRadius"), 0, 0)
    .applyMatrix4(target.bOrientation);
  settingCenter(erosB, target.scratchVector);
  target.deferentBStage
    .add(target.scratchVector)
    .applyMatrix4(target.aOrientation);

  target.mainBasis.multiplyMatrices(
    target.aOrientation,
    target.bOrientation
  );
  return target;
};

/** Phase 4E: make Eros structurally Sun-hosted without changing coordinates. */
const ErosSunRelativeOrbit = ({ children, plotMode = false }) => {
  const settings = useSettingsStore((state) => state.settings);
  const settingsByName = useMemo(
    () => new Map(settings.map((setting) => [setting.name, setting])),
    [settings]
  );
  const components = useMemo(createErosSunRelativeComponents, []);
  const rootRef = useRef();
  const centreRef = useRef();
  const carrierRef = useRef();
  const deferentBRef = useRef();
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
      updateErosSunRelativeComponents(
        components,
        settingsByName,
        modelPosition
      );
      centreRef.current?.position.copy(components.centreDifference);
      carrierRef.current?.position.copy(components.annualCarrierMismatch);
      deferentBRef.current?.position.copy(components.deferentBStage);
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
      name: EROS_SUN_RELATIVE_UPDATER_NAME,
      updateAfterMotion: update,
    });
    return () => removePlotObj(EROS_SUN_RELATIVE_UPDATER_NAME);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  return (
    <group
      ref={rootRef}
      name="Sun-Relative Eros Frame"
      matrixAutoUpdate={false}
    >
      <group ref={centreRef} name="Sun-Eros Centre Difference">
        <group ref={carrierRef} name="Sun-Eros Annual Carrier Mismatch">
          <group ref={deferentBRef} name="Eros Deferent-B Stage">
            <group ref={mainBasisRef} name="Eros Main-Orbit Basis">
              {children}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default ErosSunRelativeOrbit;
