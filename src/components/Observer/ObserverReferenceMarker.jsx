import { useEffect, useMemo } from "react";
import * as THREE from "three";
import { useObserverStore } from "./observerStore";
import { kmToUnits } from "../../utils/celestial-functions";
import createCircleTexture from "../../utils/createCircleTexture";

const REFERENCE_COLOR = "#ff2020";

export default function ObserverReferenceMarker() {
  const reference = useObserverStore((s) => s.referenceGlobalPosition);
  const texture = useMemo(() => createCircleTexture(REFERENCE_COLOR), []);
  const material = useMemo(
    () =>
      new THREE.SpriteMaterial({
        map: texture,
        color: REFERENCE_COLOR,
        transparent: true,
        depthTest: false,
        sizeAttenuation: false,
      }),
    [texture]
  );

  useEffect(
    () => () => {
      material.dispose();
      texture.dispose();
    },
    [material, texture]
  );

  if (!reference) return null;

  return (
    <sprite
      position={[
        kmToUnits(reference.x),
        kmToUnits(reference.y),
        kmToUnits(reference.z),
      ]}
      material={material}
      scale={[0.0025, 0.0025, 0.0025]}
      renderOrder={1001}
      raycast={() => null}
    />
  );
}
