import { useCallback, useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { findCelestialSetting } from "../utils/celestialSettingsSchema";

const D2R = Math.PI / 180;
export const PLUTO_ECCENTRIC_UPDATER = "Pluto Eccentric Frame Updater";

const finite = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

// THREE.RotationY(theta) maps +X toward -Z. This is the translation left by
// the former R(theta) * T(radius) * R(-theta) hierarchy after the two
// orientations cancel.
export const plutoEccentricOffset = (angle, radius) => [
  Math.cos(angle) * radius,
  0,
  -Math.sin(angle) * radius,
];

const PlutoEccentricFrame = ({ children, settingId = "pluto-eccentric", plotMode = false }) => {
  const setting = useSettingsStore(
    useCallback(
      (state) => findCelestialSetting(state.settings, settingId),
      [settingId]
    )
  );
  const posRef = useStore((state) => state.posRef);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);
  const offsetRef = useRef();

  const update = useCallback(
    (position) => {
      if (!offsetRef.current || !setting) return false;
      const angle =
        finite(setting.speed) * (Number.isFinite(position) ? position : 0) -
        finite(setting.startPos) * D2R;
      offsetRef.current.position.set(
        ...plutoEccentricOffset(angle, finite(setting.orbitRadius))
      );
      offsetRef.current.updateWorldMatrix(true, true);
      return true;
    },
    [setting]
  );

  useFrame(() => update(posRef.current));

  useEffect(() => {
    if (!plotMode) return undefined;
    addPlotObj({
      name: PLUTO_ECCENTRIC_UPDATER,
      updateAfterMotion: update,
    });
    return () => removePlotObj(PLUTO_ECCENTRIC_UPDATER);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  if (!setting) return null;

  return (
    <group
      name="Pluto Eccentric Container"
      position={[
        finite(setting.orbitCentera),
        finite(setting.orbitCenterc),
        finite(setting.orbitCenterb),
      ]}
      rotation-x={finite(setting.orbitTilta) * D2R}
      rotation-z={finite(setting.orbitTiltb) * D2R}
    >
      <group ref={offsetRef} name="Pluto Moving Eccentric Centre">
        {children}
      </group>
    </group>
  );
};

export default PlutoEccentricFrame;
