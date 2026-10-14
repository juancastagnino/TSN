import { apsidalEquantCorrection } from "./MoonApsidalEquant";

const wrap = (value) => Math.atan2(Math.sin(value), Math.cos(value));

test("is exactly neutral when its offset is zero", () => {
  expect(apsidalEquantCorrection(1.2, 0.25, 0)).toBe(0);
});

test("places the equant-defined point on the accepted lunar circle", () => {
  const meanAngle = 1.1;
  const radius = 0.25695552897999907;
  const offset = 0.01407;
  const correction = apsidalEquantCorrection(meanAngle, radius, offset);
  const centralAngle = meanAngle + correction;
  const point = [
    Math.cos(centralAngle) * radius,
    -Math.sin(centralAngle) * radius,
  ];
  const rayFromEquant = [point[0] - offset, point[1]];
  const rayAngle = Math.atan2(-rayFromEquant[1], rayFromEquant[0]);

  expect(Math.hypot(...point)).toBeCloseTo(radius, 12);
  expect(wrap(rayAngle - meanAngle)).toBeCloseTo(0, 12);
});

test("adds the expected apsidal angular action at quadrature", () => {
  const radius = 0.25695552897999907;
  const offset = 0.01407;
  const correction = apsidalEquantCorrection(
    Math.PI / 2,
    radius,
    offset
  );

  expect(correction).toBeCloseTo(-Math.asin(offset / radius), 12);
  expect(Math.abs(correction) * 180 / Math.PI).toBeCloseTo(3.139, 3);
});

test("supports the opposite equant side by changing the offset sign", () => {
  const positive = apsidalEquantCorrection(0.8, 0.25, 0.01);
  const negative = apsidalEquantCorrection(0.8, 0.25, -0.01);
  expect(negative).toBeCloseTo(-positive, 3);
});
