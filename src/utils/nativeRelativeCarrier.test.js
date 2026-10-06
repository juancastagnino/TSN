import settingsDocument from "../settings/celestial-settings.json";
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

test("evaluates the stored cosine and sine vectors at quarter phases", () => {
  const carrier = settings.get("eros-deferent-a");
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

test("requires a complete native relative carrier definition", () => {
  expect(hasNativeRelativeCarrier(settings.get("mars-deferent-e"))).toBe(true);
  expect(hasNativeRelativeCarrier(settings.get("sun-deferent"))).toBe(false);
  expect(() =>
    updateNativeRelativeCarrier(
      createNativeRelativeCarrierState(),
      settings.get("sun-deferent"),
      0
    )
  ).toThrow(/not a native relative carrier/);
});
