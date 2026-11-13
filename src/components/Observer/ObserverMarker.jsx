import { useEffect, useMemo, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useStore, useSettingsStore } from "../../store";
import { useObserverStore } from "./observerStore";
import {
  latToRad,
  longToRad,
  unitsToKm,
} from "../../utils/celestial-functions";
import createCircleTexture from "../../utils/createCircleTexture";

const center = new THREE.Vector3();
const surfaceOffset = new THREE.Vector3();
const worldOffset = new THREE.Vector3();
const worldQuaternion = new THREE.Quaternion();
const xAxis = new THREE.Vector3(1, 0, 0);
const yAxis = new THREE.Vector3(0, 1, 0);

export default function ObserverMarker() {
  const markerSystemRef = useRef(null);
  const longAxisRef = useRef(null);
  const latAxisRef = useRef(null);
  const markerRef = useRef(null);
  const targetRef = useRef(null);
  const lastPositionUpdate = useRef(0);
  const { scene } = useThree();

  const showObserver = useObserverStore((s) => s.showObserver);
  const markerColor = useObserverStore((s) => s.markerColor);
  const setCurrentGlobalPosition = useObserverStore(
    (s) => s.setCurrentGlobalPosition
  );
  const latitude = useObserverStore((s) => s.latitude);
  const longitude = useObserverStore((s) => s.longitude);
  const getSetting = useSettingsStore((s) => s.getSetting);
  const actualPlanetSizes = useStore((s) => s.actualPlanetSizes);
  const posRef = useStore((s) => s.posRef);

  const targetSettings = getSetting("Earth");
  const physicalRadius = Number(targetSettings?.actualSize || 0.00426);
  const visualRadius = actualPlanetSizes
    ? physicalRadius
    : Number(targetSettings?.size || physicalRadius);

  const texture = useMemo(
    () => createCircleTexture(markerColor),
    [markerColor]
  );
  const material = useMemo(
    () =>
      new THREE.SpriteMaterial({
        map: texture,
        color: markerColor,
        transparent: true,
        depthTest: false,
        sizeAttenuation: false,
      }),
    [texture, markerColor]
  );

  useEffect(
    () => () => {
      material.dispose();
      texture.dispose();
    },
    [material, texture]
  );

  useEffect(() => {
    const system = markerSystemRef.current;
    const target = scene.getObjectByName("Earth");
    targetRef.current = target;
    if (!system || !target) return;
    target.add(system);
    return () => {
      if (system.parent) system.parent.remove(system);
      targetRef.current = null;
    };
  }, [scene]);

  useEffect(() => {
    if (!longAxisRef.current || !latAxisRef.current || !markerRef.current)
      return;
    longAxisRef.current.rotation.y = longToRad(longitude);
    latAxisRef.current.rotation.x = latToRad(latitude);
    markerRef.current.position.y = visualRadius;
  }, [latitude, longitude, visualRadius]);

  useFrame(({ clock }) => {
    let target = targetRef.current;
    if (!target) {
      target = scene.getObjectByName("Earth");
      const system = markerSystemRef.current;
      if (target && system && system.parent !== target) target.add(system);
      targetRef.current = target || null;
    }
    if (!target || clock.elapsedTime - lastPositionUpdate.current < 0.05)
      return;
    lastPositionUpdate.current = clock.elapsedTime;

    target.updateWorldMatrix(true, false);
    target.getWorldPosition(center);
    target.getWorldQuaternion(worldQuaternion);
    surfaceOffset
      .set(0, physicalRadius, 0)
      .applyAxisAngle(xAxis, latToRad(latitude))
      .applyAxisAngle(yAxis, longToRad(longitude));
    worldOffset
      .copy(surfaceOffset)
      .applyQuaternion(worldQuaternion)
      .add(center);
    setCurrentGlobalPosition(
      {
        x: unitsToKm(worldOffset.x),
        y: unitsToKm(worldOffset.y),
        z: unitsToKm(worldOffset.z),
      },
      posRef.current
    );
  });

  return (
    <group ref={markerSystemRef} visible={showObserver}>
      <group ref={longAxisRef}>
        <group ref={latAxisRef}>
          <sprite
            ref={markerRef}
            material={material}
            scale={[0.0025, 0.0025, 0.0025]}
            renderOrder={1000}
            raycast={() => null}
          />
        </group>
      </group>
    </group>
  );
}
