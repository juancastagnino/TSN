import { useCallback, useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Quaternion, Vector3 } from "three";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { findCelestialSetting } from "../utils/celestialSettingsSchema";
import { dateTimeToPos } from "../utils/time-date-functions";

const D2R = Math.PI / 180;
const ARCSEC_TO_RAD = D2R / 3600;

// The reference is deliberately fixed and visible in the model definition.
// It is not a fitted post-processing epoch for individual stars.
export const PVP_SOLAR_ORIENTATION_REFERENCE = "2000-01-01 12:00 UTC";
const REFERENCE_POSITION = dateTimeToPos("2000-01-01", "12:00:00");
export const PVP_SOLAR_ORIENTATION_UPDATER = "PVP Solar Orientation Frame";

const number = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

// In this hierarchy the Sun is directly hosted by Earth.  Its local orbital
// vector is therefore the Earth-to-Sun vector before this frame is applied.
export const earthToSunDirectionAt = (sun, position, target = new Vector3()) => {
  const radius = number(sun?.orbitRadius);
  const angle = number(sun?.speed) * position - number(sun?.startPos) * D2R;
  return target
    .set(
      number(sun?.orbitCentera) + radius * Math.cos(angle),
      number(sun?.orbitCenterc),
      number(sun?.orbitCenterb) - radius * Math.sin(angle)
    )
    .normalize();
};

/**
 * Return the system-frame rotation for the declared Earth-Sun orientation
 * stage.  The minus sign is intentional: rotating the complete PVP hierarchy
 * is the inverse of rotating a fixed star direction in the observer frame.
 */
export const getPvpSolarOrientationQuaternion = (
  sun,
  position,
  amplitudeArcsec,
  target = new Quaternion(),
  current = new Vector3(),
  reference = new Vector3(),
  axis = new Vector3()
) => {
  earthToSunDirectionAt(sun, position, current);
  earthToSunDirectionAt(sun, REFERENCE_POSITION, reference);
  axis.subVectors(current, reference);
  const magnitude = axis.length();
  if (!Number.isFinite(magnitude) || magnitude === 0) return target.identity();

  return target.setFromAxisAngle(
    axis.multiplyScalar(1 / magnitude),
    -number(amplitudeArcsec) * ARCSEC_TO_RAD * magnitude
  );
};

const PvpSolarOrientationFrame = ({ children, plotMode = false }) => {
  const setting = useSettingsStore(
    useCallback(
      (state) => findCelestialSetting(state.settings, "pvp-solar-orientation"),
      []
    )
  );
  const sun = useSettingsStore(
    useCallback((state) => findCelestialSetting(state.settings, "sun"), [])
  );
  const posRef = useStore((state) => state.posRef);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);
  const frameRef = useRef();
  const quaternion = useMemo(() => new Quaternion(), []);
  const current = useMemo(() => new Vector3(), []);
  const reference = useMemo(() => new Vector3(), []);
  const axis = useMemo(() => new Vector3(), []);

  const update = useCallback(
    (position) => {
      if (!frameRef.current || !sun || !setting) return false;
      getPvpSolarOrientationQuaternion(
        sun,
        Number.isFinite(position) ? position : 0,
        setting.amplitude,
        quaternion,
        current,
        reference,
        axis
      );
      frameRef.current.quaternion.copy(quaternion);
      frameRef.current.updateWorldMatrix(true, true);
      return true;
    },
    [axis, current, quaternion, reference, setting, sun]
  );

  useFrame(() => update(posRef.current));

  useEffect(() => {
    if (!plotMode) return undefined;
    addPlotObj({
      name: PVP_SOLAR_ORIENTATION_UPDATER,
      updateAfterMotion: update,
      // Apply this after all positional geometry has settled for a sample.
      updatePriority: 1,
    });
    return () => removePlotObj(PVP_SOLAR_ORIENTATION_UPDATER);
  }, [addPlotObj, plotMode, removePlotObj, update]);

  return <group ref={frameRef} name="PVP Solar Orientation Frame">{children}</group>;
};

export default PvpSolarOrientationFrame;
