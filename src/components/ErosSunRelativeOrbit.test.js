import settings from "../settings/celestial-model.json";
import {
  buildSettingsIndex,
  normalizeCelestialSettings,
} from "../utils/celestialSettingsSchema";
import {
  createErosSunRelativeComponents,
  updateErosSunRelativeComponents,
} from "./ErosSunRelativeOrbit";

const byName = buildSettingsIndex(normalizeCelestialSettings(settings));

test.each([-100, -0.001, 0, 0.25, 3.75, 26, 100])(
  "evaluates Eros without an absolute parent-sized carrier at %p",
  (position) => {
    const components = updateErosSunRelativeComponents(
      createErosSunRelativeComponents(),
      byName,
      position
    );
    const carrier = byName.get("eros-deferent-a");

    expect(carrier.orbitRadius).toBe(0);
    expect(components.centreDifference.toArray()).toEqual([
      carrier.orbitCentera,
      carrier.orbitCenterc,
      carrier.orbitCenterb,
    ]);
    expect(
      components.annualCentreOffset.toArray().every(Number.isFinite)
    ).toBe(true);
    expect(components.mainBasis.elements.every(Number.isFinite)).toBe(true);
  }
);

test("represents the retained Eros annual effect as a named axial centre oscillation", () => {
  const components = updateErosSunRelativeComponents(
    createErosSunRelativeComponents(),
    byName,
    4.25
  );
  const oscillation = byName.get("eros-annual-centre-oscillation");

  expect(oscillation.amplitude).toBeGreaterThan(1);
  expect(oscillation.speed).toBeCloseTo(2 * Math.PI, 12);
  expect(components.annualCentreOffset.length()).toBeLessThanOrEqual(
    oscillation.amplitude
  );
  expect(components.annualCentreOffset.length()).toBeGreaterThan(1);
});
