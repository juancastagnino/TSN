import { useRef, useEffect, useCallback } from "react";
import { useFrame } from "@react-three/fiber";
import { useStore, usePlotStore, useSettingsStore } from "../store";

const D2R = Math.PI / 180;

const MoonOrbitalPlane = ({ children, live = false }) => {
  const outerRef = useRef();
  const innerRef = useRef();
  const posRef = useStore((state) => state.posRef);

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
    // Only the export/trace model belongs in the plot registry.
    if (live || !node) return;

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
  }, [live, node, addPlotObj, removePlotObj]);

  useFrame(() => {
    if (!live || !node || !outerRef.current || !innerRef.current) return;

    // Follow the displayed time, independently of export/trace time stepping.
    const angle = node.speed * (posRef.current ?? 0) - node.startPos * D2R;
    outerRef.current.rotation.y = angle;
    innerRef.current.rotation.y = -angle;
  });

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
