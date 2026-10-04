import { useMemo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { Vector3 } from "three";
import { useStore } from "../store";
import {
  createSunMarsBinaryState,
  updateSunMarsBinaryState,
} from "../utils/sunMarsBinaryState";

/**
 * Publishes the live visual model's exact Sun-Mars binary decomposition.
 * It observes existing objects only; it never modifies their transformations.
 */
const SunMarsBinaryTracker = () => {
  const { scene } = useThree();
  const binaryStateRef = useStore((state) => state.sunMarsBinaryStateRef);
  const binaryState = useMemo(createSunMarsBinaryState, []);
  const positions = useMemo(
    () => ({
      center: new Vector3(),
      sun: new Vector3(),
      mars: new Vector3(),
    }),
    []
  );

  useFrame(() => {
    const earth = scene.getObjectByName("Earth");
    const sun = scene.getObjectByName("Sun");
    const mars = scene.getObjectByName("Mars");

    if (!earth || !sun || !mars) {
      binaryState.valid = false;
      binaryStateRef.current = binaryState;
      return;
    }

    earth.getWorldPosition(positions.center);
    sun.getWorldPosition(positions.sun);
    mars.getWorldPosition(positions.mars);
    updateSunMarsBinaryState(
      binaryState,
      positions.center,
      positions.sun,
      positions.mars
    );
    binaryStateRef.current = binaryState;
  });

  return null;
};

export default SunMarsBinaryTracker;

