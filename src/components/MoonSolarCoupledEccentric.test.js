import { Vector3 } from "three";
import {
  composeSolarCoupledLunarOffset,
  composePairedRadialOffset,
  deriveSolarCoupledLunarAngles,
  scaleRadialProjection,
  signedAngleInEclipticXZ,
  wrapRadians,
} from "./MoonSolarCoupledEccentric";

const vectorAt = (angle) =>
  new Vector3(Math.cos(angle), 0, -Math.sin(angle));

test("paired displacement matches the projected Python construction", () => {
  const moon = vectorAt(0.7);
  const apsis = vectorAt(0.2);
  const radius = -0.007055;
  const offset = composePairedRadialOffset(moon, apsis, radius);
  expect(offset.x).toBeCloseTo(radius * (Math.cos(0.2) + Math.cos(1.2)), 12);
  expect(offset.z).toBeCloseTo(-radius * (Math.sin(0.2) + Math.sin(1.2)), 12);
  expect(offset.dot(new Vector3(-moon.z, 0, moon.x))).toBeCloseTo(0, 12);
  expect(composePairedRadialOffset(moon, apsis, 0).length()).toBe(0);
});

test("recovers signed ecliptic longitude using the Three.js Y-rotation convention", () => {
  expect(signedAngleInEclipticXZ(vectorAt(0.7))).toBeCloseTo(0.7, 12);
  expect(signedAngleInEclipticXZ(vectorAt(-1.1))).toBeCloseTo(-1.1, 12);
});

test("derives the 2D-M and pure 2D arguments from the same solar geometry", () => {
  const moonLongitude = 1.2;
  const sunLongitude = 0.25;
  const anomalisticPhase = 0.35;
  const result = deriveSolarCoupledLunarAngles(
    vectorAt(moonLongitude),
    vectorAt(sunLongitude),
    anomalisticPhase
  );
  const expectedElongation = wrapRadians(moonLongitude - sunLongitude);
  const expectedArgument = wrapRadians(
    2 * expectedElongation - anomalisticPhase
  );
  const expectedVariation = wrapRadians(2 * expectedElongation);
  expect(result.elongation).toBeCloseTo(expectedElongation, 12);
  expect(result.inequalityArgument).toBeCloseTo(expectedArgument, 12);
  expect(result.eccentricOrientation).toBeCloseTo(
    wrapRadians(moonLongitude + expectedArgument),
    12
  );
  expect(result.variationArgument).toBeCloseTo(expectedVariation, 12);
  expect(result.variationOrientation).toBeCloseTo(
    wrapRadians(moonLongitude + expectedVariation),
    12
  );
});

test("wraps the elongation continuously across the plus/minus pi boundary", () => {
  const result = deriveSolarCoupledLunarAngles(
    vectorAt(-Math.PI + 0.1),
    vectorAt(Math.PI - 0.1),
    0
  );
  expect(result.elongation).toBeCloseTo(0.2, 12);
});

test("reflects only the radial part of a solar variation displacement", () => {
  const radial = new Vector3(1, 0, 0);
  const displacement = new Vector3(2, 0, 3);
  const reflected = scaleRadialProjection(displacement, radial, -1);
  expect(reflected.x).toBeCloseTo(-2, 12);
  expect(reflected.y).toBeCloseTo(0, 12);
  expect(reflected.z).toBeCloseTo(3, 12);
});

test("combines 2D-M and 2D as translations of one lunar centre", () => {
  const moonLongitude = 0;
  const sunLongitude = -Math.PI / 4;
  const angles = deriveSolarCoupledLunarAngles(
    vectorAt(moonLongitude),
    vectorAt(sunLongitude),
    0
  );
  const offset = composeSolarCoupledLunarOffset(
    angles,
    vectorAt(moonLongitude),
    0,
    0.002168
  );

  // At D=45 degrees, 2D is 90 degrees and the variation is entirely
  // tangential. Positive amplitude advances lunar longitude in the model's
  // +Y rotation convention.
  expect(offset.x).toBeCloseTo(0, 12);
  expect(offset.y).toBeCloseTo(0, 12);
  expect(offset.z).toBeCloseTo(-0.002168, 12);
});
