import { useCallback, useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { usePlotStore, useSettingsStore, useStore } from "../store";
import { findCelestialSetting } from "../utils/celestialSettingsSchema";

const D2R = Math.PI / 180;
export const MOON_APSIDAL_EQUANT_UPDATER = "Moon Apsidal Equant Updater";

const finite = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

export const wrapEquantAngle = (value) =>
  Math.atan2(Math.sin(value), Math.cos(value));

/**
 * Return the central-angle correction produced by a classical equant.
 *
 * The lunar orbit is a circle of radius `circleRadius` centred at C. The
 * equant Q is displaced from C by `equantOffset` along `equantOrientation`.
 * Uniform phase is measured at Q; the ray from Q intersects the circle at P.
 * The returned angle rotates the ordinary C-centred circular point onto P.
 *
 * Positive angles use Three.js' Y-rotation convention: +X turns toward -Z.
 */
export const apsidalEquantCorrection = (
  meanAngle,
  circleRadius,
  equantOffset,
  equantOrientation = 0
) => {
  const radius = Math.abs(finite(circleRadius));
  const offset = finite(equantOffset);
  if (radius === 0 || offset === 0) return 0;

  const directionX = Math.cos(meanAngle);
  const directionZ = -Math.sin(meanAngle);
  const equantX = Math.cos(equantOrientation) * offset;
  const equantZ = -Math.sin(equantOrientation) * offset;
  const equantLengthSq = equantX * equantX + equantZ * equantZ;
  const projection = equantX * directionX + equantZ * directionZ;
  const discriminant =
    projection * projection + radius * radius - equantLengthSq;

  // A physically useful equant must remain inside its circle. Returning zero
  // avoids injecting invalid coordinates while the author edits parameters.
  if (discriminant < 0) return 0;

  const rayDistance = -projection + Math.sqrt(discriminant);
  const pointX = equantX + rayDistance * directionX;
  const pointZ = equantZ + rayDistance * directionZ;
  const centralAngle = Math.atan2(-pointZ, pointX);
  return wrapEquantAngle(centralAngle - meanAngle);
};

const MoonApsidalEquant = ({
  children,
  settingId = "moon-apsidal-equant",
  targetName = "Moon",
  plotMode = false,
}) => {
  const setting = useSettingsStore(
    useCallback(
      (state) => findCelestialSetting(state.settings, settingId),
      [settingId]
    )
  );
  const moon = useSettingsStore(
    useCallback(
      (state) => findCelestialSetting(state.settings, "moon"),
      []
    )
  );
  const posRef = useStore((state) => state.posRef);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);
  const frameRef = useRef();
  const updaterName = `${MOON_APSIDAL_EQUANT_UPDATER}:${targetName}`;

  const update = useCallback(
    (position) => {
      if (!frameRef.current || !setting || !moon) return false;
      const modelPosition = Number.isFinite(position) ? position : 0;
      const meanAngle =
        finite(moon.speed) * modelPosition - finite(moon.startPos) * D2R;
      frameRef.current.rotation.y = apsidalEquantCorrection(
        meanAngle,
        moon.orbitRadius,
        setting.orbitRadius,
        finite(setting.startPos) * D2R
      );
      frameRef.current.updateWorldMatrix(true, true);
      return true;
    },
    [moon, setting]
  );

  // Establish the equant-defined lunar angle before the solar-coupled frame
  // samples the Earth-Moon direction for the same instant.
  useFrame(() => update(posRef.current), -1);

  useEffect(() => {
    if (!plotMode) return undefined;
    addPlotObj({
      name: updaterName,
      updateAfterMotion: update,
      updatePriority: -1,
    });
    return () => removePlotObj(updaterName);
  }, [addPlotObj, plotMode, removePlotObj, update, updaterName]);

  if (!setting || !moon) return null;

  return (
    <group ref={frameRef} name={`${targetName} Apsidal Equant Frame`}>
      {children}
    </group>
  );
};

export default MoonApsidalEquant;
