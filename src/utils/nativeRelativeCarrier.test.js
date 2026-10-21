import settingsDocument from "../settings/celestial-model.json";
import {
  buildSettingsIndex,
  normalizeCelestialSettings,
} from "./celestialSettingsSchema";
import {
  createNativeRelativeCarrierState,
  hasNativeRelativeCarrier,
  updateNativeRelativeCarrier,
} from "./nativeRelativeCarrier";

const settings = buildSettingsIndex(
  normalizeCelestialSettings(settingsDocument)
);

test("evaluates cosine and sine vectors at quarter phases", () => {
  // Exercise the generic evaluator with an explicit fixture: the current Eros
  // model no longer stores the former annual residual fields.
  const carrier = {
    ...settings.get("eros-deferent-a"),
    relativeAnnualSpeed: 2 * Math.PI,
    relativeAnnualCosX: 0.1,
    relativeAnnualCosY: -0.2,
    relativeAnnualCosZ: 0.3,
    relativeAnnualSinX: -0.4,
    relativeAnnualSinY: 0.5,
    relativeAnnualSinZ: -0.6,
  };
  const state = createNativeRelativeCarrierState();
  const quarter = Math.PI / (2 * carrier.relativeAnnualSpeed);

  updateNativeRelativeCarrier(state, carrier, 0);
  expect(state.annualResidual.toArray()).toEqual([
    carrier.relativeAnnualCosX,
    carrier.relativeAnnualCosY,
    carrier.relativeAnnualCosZ,
  ]);

  updateNativeRelativeCarrier(state, carrier, quarter);
  expect(state.annualResidual.x).toBeCloseTo(carrier.relativeAnnualSinX, 12);
  expect(state.annualResidual.y).toBeCloseTo(carrier.relativeAnnualSinY, 12);
  expect(state.annualResidual.z).toBeCloseTo(carrier.relativeAnnualSinZ, 12);
});

test("treats an omitted annual harmonic as an exact zero vector", () => {
  const mars = settings.get("mars-deferent-e");
  const state = createNativeRelativeCarrierState();
  expect(hasNativeRelativeCarrier(mars)).toBe(true);
  expect(mars.relativeAnnualSpeed).toBeUndefined();
  updateNativeRelativeCarrier(state, mars, 123.5);
  expect(state.annualResidual.toArray()).toEqual([0, 0, 0]);
  expect(() =>
    updateNativeRelativeCarrier(createNativeRelativeCarrierState(), undefined, 0)
  ).toThrow(/not a native relative carrier/);
});
