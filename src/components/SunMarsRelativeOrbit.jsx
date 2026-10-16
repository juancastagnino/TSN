import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { buildSettingsIndex } from "../utils/celestialSettingsSchema";
import {
  createNativeRelativeCarrierState,
  updateNativeRelativeCarrier,
} from "../utils/nativeRelativeCarrier";

export const SUN_MARS_FRAME_NAME = "Sun-Mars Binary Frame";
export const SUN_MARS_RELATIVE_UPDATER_NAME =
  "Mars Binary Geometry";

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
  annualFrameResidual: new Vector3(),
  longPeriodPosition: new Vector3(),
  mainBasis: new Matrix4(),
  annualFrameState: createNativeRelativeCarrierState(),
  annualOrientation: new Matrix4(),
  longPeriodOrientation: new Matrix4(),
  scratchMatrix: new Matrix4(),
  scratchVectorA: new Vector3(),
});

/**
 * Evaluate the native Sun-relative Mars geometry.
 *
 * The Binary Annual Frame establishes the fixed Sun-relative centre and annual
 * orientation. The Long-Period Deferent then contributes its smaller rotating
 * centre before the main Mars orbit is evaluated. Their stable historical IDs
 * remain import-compatible even though the displayed names now describe their
 * geometric roles.
 */
export const updateSunMarsRelativeComponents = (
  target,
  settingsByName,
  position
) => {
  const get = (id) =>
    settingsByName instanceof Map
      ? settingsByName.get(id)
      : settingsByName[id];
  // Stable IDs are retained for settings-file compatibility. In schema v3 the
  // two stages are presented as the Binary Annual Frame and Long-Period
  // Deferent rather than as the opaque historical E/S pair.
  const binaryAnnualFrame = get("mars-deferent-e");
  const longPeriodDeferent = get("mars-deferent-s");

  updateNativeRelativeCarrier(
    target.annualFrameState,
    binaryAnnualFrame,
    position
  );
  target.centreDifference.copy(target.annualFrameState.centre);
  target.annualFrameResidual.copy(target.annualFrameState.annualResidual);
  target.annualOrientation.copy(target.annualFrameState.orientation);
  orbitalOrientation(
    longPeriodDeferent,
    position,
    target.longPeriodOrientation,
    target.scratchMatrix
  );
  target.longPeriodPosition
    .set(number(longPeriodDeferent, "orbitRadius"), 0, 0)
    .applyMatrix4(target.longPeriodOrientation);
  settingCenter(longPeriodDeferent, target.scratchVectorA);
  target.longPeriodPosition
    .add(target.scratchVectorA)
    .applyMatrix4(target.annualOrientation);

  target.mainBasis.multiplyMatrices(
    target.annualOrientation,
    target.longPeriodOrientation
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
 * Native binary-companion branch. Mars still supplies its main local orbit, so
 * Phobos and Deimos inherit the completed Mars frame.
 */
const SunMarsRelativeOrbit = ({ children, plotMode = false }) => {
  const settings = useSettingsStore((state) => state.settings);
  const settingsByName = useMemo(() => buildSettingsIndex(settings), [settings]);
  const components = useMemo(createSunMarsRelativeComponents, []);
  const rootRef = useRef();
  const centreRef = useRef();
  const annualResidualRef = useRef();
  const longPeriodPositionRef = useRef();
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
      annualResidualRef.current?.position.copy(components.annualFrameResidual);
      longPeriodPositionRef.current?.position.copy(
        components.longPeriodPosition
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
      name: SUN_MARS_RELATIVE_UPDATER_NAME,
      updateAfterMotion: update,
    });
    return () => removePlotObj(SUN_MARS_RELATIVE_UPDATER_NAME);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  return (
    <group
      ref={rootRef}
      name="Mars Binary Geometry"
      matrixAutoUpdate={false}
    >
      <group ref={centreRef} name="Mars Binary Reference Centre">
        <group ref={annualResidualRef} name="Mars Annual-Frame Residual">
          <group
            ref={longPeriodPositionRef}
            name="Mars Long-Period Deferent Position"
          >
            <group
              ref={mainBasisRef}
              name="Mars Combined Orbital Orientation"
            >
              {children}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default SunMarsRelativeOrbit;
