import { useRef, useEffect, useCallback } from "react";
import { usePlotStore, useSettingsStore } from "../store";

const D2R = Math.PI / 180;

const MoonOrbitalPlane = ({ children }) => {
  const outerRef = useRef();
  const innerRef = useRef();

  const node = useSettingsStore(
    useCallback(
      (state) => state.settings.find((p) => p.name === "Moon Node"),
      []
    )
  );

  const plane = useSettingsStore(
    useCallback(
      (state) => state.settings.find((p) => p.name === "Moon Plane"),
      []
    )
  );

  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);

  useEffect(() => {
    if (!node) return;

    // Outer rotation: +Omega(t)
    addPlotObj({
      name: "Moon Node Outer",
      speed: node.speed,
      startPos: node.startPos,
      orbitRef: outerRef,
    });

    // Inner counter-rotation: -Omega(t)
    addPlotObj({
      name: "Moon Node Inner",
      speed: -node.speed,
      startPos: -node.startPos,
      orbitRef: innerRef,
    });

    return () => {
      removePlotObj("Moon Node Outer");
      removePlotObj("Moon Node Inner");
    };
  }, [node, addPlotObj, removePlotObj]);

  if (!node || !plane) return null;

  return (
    <group ref={outerRef}>
      <group
        rotation-x={(plane.orbitTilta || 0) * D2R}
        rotation-z={(plane.orbitTiltb || 0) * D2R}
      >
        <group ref={innerRef}>
          {children}
        </group>
      </group>
    </group>
  );
};

export default MoonOrbitalPlane;