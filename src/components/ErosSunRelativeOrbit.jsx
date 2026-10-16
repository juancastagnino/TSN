import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { buildSettingsIndex } from "../utils/celestialSettingsSchema";
import {
  createNativeRelativeCarrierState,
  updateNativeRelativeCarrier,
} from "../utils/nativeRelativeCarrier";
import {
  SUN_MARS_FRAME_NAME,
  updateSunRelativeFrame,
} from "./SunMarsRelativeOrbit";

export const EROS_SUN_RELATIVE_UPDATER_NAME =
  "Eros Sun-Relative Geometry";

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
  annualCentreOffset: new Vector3(),
  localDeferentPosition: new Vector3(),
  mainBasis: new Matrix4(),
  annualFrameState: createNativeRelativeCarrierState(),
  annualOrientation: new Matrix4(),
  localDeferentOrientation: new Matrix4(),
  scratchMatrix: new Matrix4(),
  scratchVector: new Vector3(),
});

const updateAnnualCentreOffset = (target, setting, position) => {
  const axis = target.scratchVector.set(
    number(setting, "axisX"),
    number(setting, "axisY"),
    number(setting, "axisZ")
  );
  if (axis.lengthSq() === 0) {
    target.annualCentreOffset.set(0, 0, 0);
    return;
  }
  const angle =
    number(setting, "speed") * position - number(setting, "phase") * D2R;
  target.annualCentreOffset
    .copy(axis.normalize())
    .multiplyScalar(number(setting, "amplitude") * Math.cos(angle));
};

/**
 * Evaluate the native Sun-relative Eros chain. The Sun-Relative Annual Frame
 * stores a direct centre and its orientation. A separately declared annual
 * axial displacement then moves that centre without rotating Eros's orbit.
 * The Local Deferent and Eros orbit remain local geometric stages.
 */
export const updateErosSunRelativeComponents = (
  target,
  settingsByName,
  position
) => {
  const get = (id) =>
    settingsByName instanceof Map
      ? settingsByName.get(id)
      : settingsByName[id];
  // Stable IDs preserve compatibility with historical settings exports.
  const sunRelativeAnnualFrame = get("eros-deferent-a");
  const annualCentreOscillation = get("eros-annual-centre-oscillation");
  const localDeferent = get("eros-deferent-b");

  updateNativeRelativeCarrier(
    target.annualFrameState,
    sunRelativeAnnualFrame,
    position
  );
  target.centreDifference.copy(target.annualFrameState.centre);
  updateAnnualCentreOffset(
    target,
    annualCentreOscillation,
    position
  );
  target.annualOrientation.copy(target.annualFrameState.orientation);
  orbitalOrientation(
    localDeferent,
    position,
    target.localDeferentOrientation,
    target.scratchMatrix
  );
  target.localDeferentPosition
    .set(number(localDeferent, "orbitRadius"), 0, 0)
    .applyMatrix4(target.localDeferentOrientation);
  settingCenter(localDeferent, target.scratchVector);
  target.localDeferentPosition
    .add(target.scratchVector)
    .applyMatrix4(target.annualOrientation);

  target.mainBasis.multiplyMatrices(
    target.annualOrientation,
    target.localDeferentOrientation
  );
  return target;
};

/** Native parent-relative Eros branch. */
const ErosSunRelativeOrbit = ({ children, plotMode = false }) => {
  const settings = useSettingsStore((state) => state.settings);
  const settingsByName = useMemo(() => buildSettingsIndex(settings), [settings]);
  const components = useMemo(createErosSunRelativeComponents, []);
  const rootRef = useRef();
  const centreRef = useRef();
  const annualCentreOffsetRef = useRef();
  const localDeferentRef = useRef();
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
      annualCentreOffsetRef.current?.position.copy(
        components.annualCentreOffset
      );
      localDeferentRef.current?.position.copy(
        components.localDeferentPosition
      );
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
      name="Eros Sun-Relative Geometry"
      matrixAutoUpdate={false}
    >
      <group ref={centreRef} name="Eros Sun-Relative Centre">
        <group
          ref={annualCentreOffsetRef}
          name="Eros Annual Centre Oscillation"
        >
          <group ref={localDeferentRef} name="Eros Local Deferent Position">
            <group ref={mainBasisRef} name="Eros Combined Orbital Orientation">
              {children}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default ErosSunRelativeOrbit;
