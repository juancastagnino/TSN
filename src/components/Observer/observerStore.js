import { create } from "zustand";

const emptyPosition = { x: 0, y: 0, z: 0 };

export const useObserverStore = create((set, get) => ({
  showObserver: false,
  setShowObserver: (value) => set({ showObserver: value }),
  traceObserver: false,
  setTraceObserver: (value) => set({ traceObserver: value }),
  latitude: 0,
  setLatitude: (value) =>
    set({ latitude: Math.max(-90, Math.min(90, Number(value) || 0)) }),
  longitude: 0,
  setLongitude: (value) => {
    const number = Number(value) || 0;
    set({ longitude: ((((number + 180) % 360) + 360) % 360) - 180 });
  },
  markerColor: "#00ffff",
  setMarkerColor: (value) => set({ markerColor: value }),
  traceColor: "#00ffff",
  setTraceColor: (value) => set({ traceColor: value }),
  currentGlobalPosition: emptyPosition,
  referenceGlobalPosition: null,
  referenceTime: null,
  displacementKm: 0,
  setCurrentGlobalPosition: (position) => {
    const reference = get().referenceGlobalPosition;
    const displacementKm = reference
      ? Math.hypot(
          position.x - reference.x,
          position.y - reference.y,
          position.z - reference.z
        )
      : 0;
    set({ currentGlobalPosition: position, displacementKm });
  },
  captureReference: (time = null) => {
    const current = get().currentGlobalPosition;
    set({
      referenceGlobalPosition: { ...current },
      referenceTime: time,
      displacementKm: 0,
    });
  },
  clearReference: () =>
    set({
      referenceGlobalPosition: null,
      referenceTime: null,
      displacementKm: 0,
    }),
}));
