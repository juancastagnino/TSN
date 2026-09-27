import { useCallback, useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { usePlotStore, useSettingsStore, useStore } from "../store";

const D2R = Math.PI / 180;
const number = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

// Applies a rotating displacement while counter-rotating the child frame.
// With a zero radius this is exactly an identity transform, regardless of
// speed/phase.  With a non-zero radius, offset phase and child orbital phase
// remain independent.
const CounterRotatedOrbit = ({ name, children, live = false }) => {
  const settings = useSettingsStore(
    useCallback(
      (state) => state.settings.find((item) => item.name === name),
      [name]
    )
  );
  const posRef = useStore((state) => state.posRef);
  const addPlotObj = usePlotStore((state) => state.addPlotObj);
  const removePlotObj = usePlotStore((state) => state.removePlotObj);
  const outerRef = useRef();
  const innerRef = useRef();

  const speed = number(settings?.speed);
  const startPos = number(settings?.startPos);

  useEffect(() => {
    if (live || !settings) return undefined;

    addPlotObj({
      name: `${name} Outer`,
      speed,
      startPos,
      orbitRef: outerRef,
    });
    addPlotObj({
      name: `${name} Inner`,
      speed: -speed,
      startPos: -startPos,
      orbitRef: innerRef,
    });

    return () => {
      removePlotObj(`${name} Outer`);
      removePlotObj(`${name} Inner`);
    };
  }, [live, settings, name, speed, startPos, addPlotObj, removePlotObj]);

  useFrame(() => {
    if (!live || !outerRef.current || !innerRef.current) return;
    const angle = speed * (posRef.current ?? 0) - startPos * D2R;
    outerRef.current.rotation.y = angle;
    innerRef.current.rotation.y = -angle;
  });

  if (!settings) return null;

  return (
    <group
      position={[
        number(settings.orbitCentera),
        number(settings.orbitCenterc),
        number(settings.orbitCenterb),
      ]}
      rotation-x={number(settings.orbitTilta) * D2R}
      rotation-z={number(settings.orbitTiltb) * D2R}
    >
      <group ref={outerRef}>
        <group position={[number(settings.orbitRadius), 0, 0]}>
          <group ref={innerRef}>{children}</group>
        </group>
      </group>
    </group>
  );
};

export default CounterRotatedOrbit;
