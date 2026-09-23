import { useEffect, useRef } from "react";
import { Vector3 } from "three";
import { useStore, usePlotStore, useSettingsStore } from "../../store";
import { useObserverStore } from "./observerStore";
import { useTraceStore } from "../Trace/traceStore";
import { getObserverLocalPosition } from "./observerPosition";
import TraceLine from "../Trace/TraceLine";
import useFrameInterval from "../../utils/useFrameInterval";

const localPosition = new Vector3();
const DEG2RAD = Math.PI / 180;
const BASE_MAX_POINTS = 5000;

export default function ObserverTrace() {
  const plotObjects = usePlotStore((s) => s.plotObjects);
  const posRef = useStore((s) => s.posRef);
  const speedFact = useStore((s) => s.speedFact);
  const speedMultiplier = useStore((s) => s.speedMultiplier);
  const latitude = useObserverStore((s) => s.latitude);
  const longitude = useObserverStore((s) => s.longitude);
  const traceObserver = useObserverStore((s) => s.traceObserver);
  const traceColor = useObserverStore((s) => s.traceColor);
  const { lineWidth, dotted, interval, lengthMultiplier } = useTraceStore();
  const getSetting = useSettingsStore((s) => s.getSetting);

  const traceLength = Math.max(
    2,
    Math.round(BASE_MAX_POINTS * lengthMultiplier)
  );
  const sampleStep = Math.max(
    Number.EPSILON,
    Math.abs(Number(speedFact) * Number(speedMultiplier || 1))
  );
  const pointsArrRef = useRef(new Float32Array(traceLength * 3));
  const pointCountRef = useRef(0);
  const sampleTimeRef = useRef(null);

  useEffect(() => {
    pointsArrRef.current = new Float32Array(traceLength * 3);
    pointCountRef.current = 0;
    sampleTimeRef.current = null;
  }, [traceObserver, traceLength, sampleStep, latitude, longitude]);

  useFrameInterval(() => {
    if (!traceObserver || plotObjects.length === 0) return;

    const targetObj = plotObjects.find((p) => p.name === "Earth");
    const settings = getSetting("Earth");
    if (
      !targetObj?.orbitRef?.current ||
      !targetObj?.cSphereRef?.current ||
      !settings
    )
      return;

    const liveTime = posRef.current || 0;
    if (sampleTimeRef.current === null || liveTime < sampleTimeRef.current) {
      sampleTimeRef.current = liveTime;
      pointCountRef.current = 0;
    }

    const appendPosition = (sampleTime) => {
      targetObj.orbitRef.current.rotation.y =
        Number(targetObj.speed || 0) * sampleTime -
        Number(targetObj.startPos || 0) * DEG2RAD;
      targetObj.cSphereRef.current.updateWorldMatrix(true, false);

      getObserverLocalPosition({
        latitude,
        longitude,
        radius: Number(settings.actualSize || 0.00426),
        time: sampleTime,
        rotationStart: settings.rotationStart,
        rotationSpeed: settings.rotationSpeed,
        target: localPosition,
      });
      targetObj.cSphereRef.current.localToWorld(localPosition);

      if (pointCountRef.current >= traceLength) {
        pointsArrRef.current.copyWithin(0, 3);
        pointCountRef.current = traceLength - 1;
      }
      const offset = pointCountRef.current * 3;
      pointsArrRef.current[offset] = localPosition.x;
      pointsArrRef.current[offset + 1] = localPosition.y;
      pointsArrRef.current[offset + 2] = localPosition.z;
      pointCountRef.current++;
    };

    if (pointCountRef.current === 0) appendPosition(sampleTimeRef.current);

    const startedAt = performance.now();
    while (
      liveTime - sampleTimeRef.current >= sampleStep * (1 - 1e-9) &&
      performance.now() - startedAt < 50
    ) {
      sampleTimeRef.current += sampleStep;
      appendPosition(sampleTimeRef.current);
    }

    targetObj.orbitRef.current.rotation.y =
      Number(targetObj.speed || 0) * liveTime -
      Number(targetObj.startPos || 0) * DEG2RAD;
    targetObj.cSphereRef.current.updateWorldMatrix(true, false);
  }, interval);

  if (!traceObserver) return null;

  return (
    <TraceLine
      pointsArrRef={pointsArrRef}
      pointCountRef={pointCountRef}
      traceLength={traceLength}
      color={traceColor}
      dots={dotted}
      lineWidth={lineWidth}
      interval={interval}
    />
  );
}
