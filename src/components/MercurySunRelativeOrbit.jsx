import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import {
  SUN_MARS_FRAME_NAME,
  updateSunRelativeFrame,
} from "./SunMarsRelativeOrbit";

export const MERCURY_SUN_RELATIVE_UPDATER_NAME =
  "Mercury Sun-Relative Components";

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

export const createMercurySunRelativeComponents = () => ({
  centreDifference: new Vector3(),
  annualCarrierMismatch: new Vector3(),
  deferentBStage: new Vector3(),
  planeStage: new Vector3(),
  mainBasis: new Matrix4(),
  aOrientation: new Matrix4(),
  bOrientation: new Matrix4(),
  planeOrientation: new Matrix4(),
  sunDeferentOrientation: new Matrix4(),
  sunOrientation: new Matrix4(),
  abBasis: new Matrix4(),
  scratchMatrix: new Matrix4(),
  scratchVector: new Vector3(),
});

/**
 * Expand the legacy Mercury chain into the five exact Phase 4A terms.
 *
 * Mercury deferent B currently has zero orbital radius, but its centre and
 * orientation remain active and are deliberately retained in deferentBStage.
 * The unchanged Mercury leaf supplies the fifth term beneath mainBasis.
 */
export const updateMercurySunRelativeComponents = (
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
  const mercuryA = get("Mercury deferent A");
  const mercuryB = get("Mercury deferent B");
  const mercuryPlane = get("Mercury Plane");

  orbitalOrientation(
    mercuryA,
    position,
    target.aOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    mercuryB,
    position,
    target.bOrientation,
    target.scratchMatrix
  );
  orbitalOrientation(
    mercuryPlane,
    position,
    target.planeOrientation,
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
  settingCenter(mercuryA, target.centreDifference);
  settingCenter(sunDeferent, target.scratchVector);
  target.centreDifference.sub(target.scratchVector);
  settingCenter(sun, target.scratchVector).applyMatrix4(
    target.sunDeferentOrientation
  );
  target.centreDifference.sub(target.scratchVector);

  // QA*rA - QD*rD - QD*QSun*rSun
  target.annualCarrierMismatch
    .set(number(mercuryA, "orbitRadius"), 0, 0)
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

  // QA*(cB + QB*rB). The zero rB does not remove the transformed cB.
  target.deferentBStage
    .set(number(mercuryB, "orbitRadius"), 0, 0)
    .applyMatrix4(target.bOrientation);
  settingCenter(mercuryB, target.scratchVector);
  target.deferentBStage
    .add(target.scratchVector)
    .applyMatrix4(target.aOrientation);

  // QA*QB*(cPlane + QPlane*rPlane)
  target.planeStage
    .set(number(mercuryPlane, "orbitRadius"), 0, 0)
    .applyMatrix4(target.planeOrientation);
  settingCenter(mercuryPlane, target.scratchVector);
  target.planeStage
    .add(target.scratchVector)
    .applyMatrix4(target.bOrientation)
    .applyMatrix4(target.aOrientation);

  target.abBasis.multiplyMatrices(
    target.aOrientation,
    target.bOrientation
  );
  target.mainBasis.multiplyMatrices(
    target.abBasis,
    target.planeOrientation
  );
  return target;
};

/** Phase 4C: make Mercury structurally Sun-hosted without changing coordinates. */
const MercurySunRelativeOrbit = ({ children, plotMode = false }) => {
  const settings = useSettingsStore((state) => state.settings);
  const settingsByName = useMemo(
    () => new Map(settings.map((setting) => [setting.name, setting])),
    [settings]
  );
  const components = useMemo(createMercurySunRelativeComponents, []);
  const rootRef = useRef();
  const centreRef = useRef();
  const carrierRef = useRef();
  const deferentBRef = useRef();
  const planeRef = useRef();
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
      updateMercurySunRelativeComponents(
        components,
        settingsByName,
        modelPosition
      );
      centreRef.current?.position.copy(components.centreDifference);
      carrierRef.current?.position.copy(components.annualCarrierMismatch);
      deferentBRef.current?.position.copy(components.deferentBStage);
      planeRef.current?.position.copy(components.planeStage);
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
      name: MERCURY_SUN_RELATIVE_UPDATER_NAME,
      updateAfterMotion: update,
    });
    return () => removePlotObj(MERCURY_SUN_RELATIVE_UPDATER_NAME);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  return (
    <group
      ref={rootRef}
      name="Sun-Relative Mercury Frame"
      matrixAutoUpdate={false}
    >
      <group ref={centreRef} name="Sun-Mercury Centre Difference">
        <group ref={carrierRef} name="Sun-Mercury Annual Carrier Mismatch">
          <group ref={deferentBRef} name="Mercury Deferent-B Stage">
            <group ref={planeRef} name="Mercury Fixed-Plane Stage">
              <group ref={mainBasisRef} name="Mercury Main-Orbit Basis">
                {children}
              </group>
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default MercurySunRelativeOrbit;
