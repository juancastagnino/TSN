import { useEffect, useRef } from "react";
import { useStore } from "../../store";
import { useObserverStore } from "./observerStore";
import { useTraceStore } from "../Trace/traceStore";
import { kmToUnits } from "../../utils/celestial-functions";
import TraceLine from "../Trace/TraceLine";
import useFrameInterval from "../../utils/useFrameInterval";

const BASE_MAX_POINTS = 5000;

export default function ObserverTrace() {
  const speedFact = useStore((s) => s.speedFact);
  const speedMultiplier = useStore((s) => s.speedMultiplier);
  const latitude = useObserverStore((s) => s.latitude);
  const longitude = useObserverStore((s) => s.longitude);
  const traceObserver = useObserverStore((s) => s.traceObserver);
  const traceColor = useObserverStore((s) => s.traceColor);
  const { lineWidth, dotted, interval, lengthMultiplier } = useTraceStore();

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
  const lastRecordedTimeRef = useRef(null);

  useEffect(() => {
    pointsArrRef.current = new Float32Array(traceLength * 3);
    pointCountRef.current = 0;
    lastRecordedTimeRef.current = null;
  }, [traceObserver, traceLength, sampleStep, latitude, longitude]);

  useFrameInterval(() => {
    if (!traceObserver) return;

    const observerState = useObserverStore.getState();
    const position = observerState.currentGlobalPosition;
    const positionTime = observerState.currentPositionTime;
    if (!position || positionTime === null) return;

    const previousTime = lastRecordedTimeRef.current;
    const isRunning = useStore.getState().run;
    const elapsed =
      previousTime === null ? Infinity : Math.abs(positionTime - previousTime);

    // Manual calendar steps (month/year) have variable durations. When the
    // simulation is paused, every distinct user step is one valid sample.
    // During animation, retain the selected general step as the cadence.
    const shouldAppend =
      previousTime === null ||
      (!isRunning && positionTime !== previousTime) ||
      (isRunning && elapsed >= sampleStep * (1 - 1e-9));
    if (!shouldAppend) return;

    if (pointCountRef.current >= traceLength) {
      pointsArrRef.current.copyWithin(0, 3);
      pointCountRef.current = traceLength - 1;
    }

    const offset = pointCountRef.current * 3;
    pointsArrRef.current[offset] = kmToUnits(position.x);
    pointsArrRef.current[offset + 1] = kmToUnits(position.y);
    pointsArrRef.current[offset + 2] = kmToUnits(position.z);
    pointCountRef.current++;
    lastRecordedTimeRef.current = positionTime;
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
