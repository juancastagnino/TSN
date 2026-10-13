import { Matrix4, Vector3 } from "three";
import { plutoEccentricOffset } from "./PlutoEccentricFrame";

test("reproduces the translation left by rotation, radius and counterrotation", () => {
  const angle = 1.234;
  const radius = 134.260927266641;
  const legacy = new Vector3(radius, 0, 0).applyMatrix4(
    new Matrix4().makeRotationY(angle)
  );
  const direct = new Vector3(...plutoEccentricOffset(angle, radius));
  expect(direct.x).toBeCloseTo(legacy.x, 12);
  expect(direct.y).toBeCloseTo(legacy.y, 12);
  expect(direct.z).toBeCloseTo(legacy.z, 12);
});

test("does not encode a second independent rotation", () => {
  expect(plutoEccentricOffset(0, 2)).toEqual([2, 0, -0]);
  const quarterTurn = plutoEccentricOffset(Math.PI / 2, 2);
  expect(quarterTurn[0]).toBeCloseTo(0, 12);
  expect(quarterTurn[2]).toBeCloseTo(-2, 12);
});

test("preserves both legacy child position and child orientation", () => {
  const angle = -0.73;
  const radius = 17.25;
  const childPoint = new Vector3(4, -2, 9);
  const legacy = new Matrix4()
    .makeRotationY(angle)
    .multiply(new Matrix4().makeTranslation(radius, 0, 0))
    .multiply(new Matrix4().makeRotationY(-angle));
  const direct = new Matrix4().makeTranslation(
    ...plutoEccentricOffset(angle, radius)
  );
  const legacyPoint = childPoint.clone().applyMatrix4(legacy);
  const directPoint = childPoint.clone().applyMatrix4(direct);
  expect(directPoint.x).toBeCloseTo(legacyPoint.x, 12);
  expect(directPoint.y).toBeCloseTo(legacyPoint.y, 12);
  expect(directPoint.z).toBeCloseTo(legacyPoint.z, 12);
});
