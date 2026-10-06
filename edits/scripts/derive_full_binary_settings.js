/*
 * Read-only migration audit for full-binary-tychos.
 *
 * The frozen source values below are the accepted absolute A/E carriers from
 * the parent native-binary-system baseline. The script derives their exact
 * Sun-relative centre and annual harmonic, then verifies that the current
 * direct settings reproduce both over a 200-model-year grid.
 */

const fs = require("fs");
const path = require("path");
const { Matrix4, Vector3 } = require("three");

const ROOT = path.resolve(__dirname, "../..");
const currentDocument = JSON.parse(
  fs.readFileSync(
    path.join(ROOT, "src/settings/celestial-settings.json"),
    "utf8"
  )
);
const current = new Map(
  currentDocument.settings.map((setting) => [setting.id, setting])
);

const legacy = new Map(
  [
    {
      id: "sun-deferent",
      startPos: 0,
      speed: 0,
      orbitRadius: 0,
      orbitCentera: 0,
      orbitCenterb: 0,
      orbitCenterc: 0,
      orbitTilta: 0,
      orbitTiltb: 0,
    },
    {
      id: "sun",
      startPos: 0,
      speed: 6.283185307179586,
      orbitRadius: 100,
      orbitCentera: 3.3,
      orbitCenterb: -0.645,
      orbitCenterc: 0,
      orbitTilta: 0.2762,
      orbitTiltb: 0,
    },
    {
      id: "mars-deferent-e",
      startPos: 0,
      speed: 6.283185307179586,
      orbitRadius: 100,
      orbitCentera: 10.1,
      orbitCenterb: -20.7,
      orbitCenterc: 0,
      orbitTilta: 0,
      orbitTiltb: 0,
    },
    {
      id: "mercury-deferent-a",
      startPos: 0,
      speed: 6.283185307179586,
      orbitRadius: 100,
      orbitCentera: 2,
      orbitCenterb: 2,
      orbitCenterc: -0.5,
      orbitTilta: 0,
      orbitTiltb: 0,
    },
    {
      id: "venus-deferent-a",
      startPos: 0,
      speed: 6.283185307179586,
      orbitRadius: 100,
      orbitCentera: 0,
      orbitCenterb: 0,
      orbitCenterc: 0,
      orbitTilta: 0,
      orbitTiltb: 0,
    },
    {
      id: "eros-deferent-a",
      startPos: 0,
      speed: 6.283185307179586,
      orbitRadius: 100,
      orbitCentera: -40,
      orbitCenterb: 31.5,
      orbitCenterc: -0.5,
      orbitTilta: -7.3,
      orbitTiltb: 3.6,
    },
  ].map((setting) => [setting.id, setting])
);

const D2R = Math.PI / 180;
const number = (setting, key) => Number(setting?.[key] || 0);
const centre = (setting) =>
  new Vector3(
    number(setting, "orbitCentera"),
    number(setting, "orbitCenterc"),
    number(setting, "orbitCenterb")
  );

const orientation = (setting, position) =>
  new Matrix4()
    .makeRotationX(number(setting, "orbitTilta") * D2R)
    .multiply(
      new Matrix4().makeRotationZ(number(setting, "orbitTiltb") * D2R)
    )
    .multiply(
      new Matrix4().makeRotationY(
        number(setting, "speed") * position -
          number(setting, "startPos") * D2R
      )
    );

const orbitVector = (setting, position) =>
  new Vector3(number(setting, "orbitRadius"), 0, 0).applyMatrix4(
    orientation(setting, position)
  );

const legacyRelative = (carrierId, position) => {
  const carrier = legacy.get(carrierId);
  const sunDeferent = legacy.get("sun-deferent");
  const sun = legacy.get("sun");
  const sunDeferentOrientation = orientation(sunDeferent, position);

  return {
    centre: centre(carrier)
      .sub(centre(sunDeferent))
      .sub(centre(sun).applyMatrix4(sunDeferentOrientation)),
    annual: orbitVector(carrier, position)
      .sub(orbitVector(sunDeferent, position))
      .sub(orbitVector(sun, position).applyMatrix4(sunDeferentOrientation)),
  };
};

const directRelative = (setting, position) => {
  const angle =
    number(setting, "relativeAnnualSpeed") * position -
    number(setting, "relativeAnnualStart") * D2R;
  const annual = new Vector3(
    number(setting, "relativeAnnualCosX"),
    number(setting, "relativeAnnualCosY"),
    number(setting, "relativeAnnualCosZ")
  )
    .multiplyScalar(Math.cos(angle))
    .addScaledVector(
      new Vector3(
        number(setting, "relativeAnnualSinX"),
        number(setting, "relativeAnnualSinY"),
        number(setting, "relativeAnnualSinZ")
      ),
      Math.sin(angle)
    );
  return { centre: centre(setting), annual };
};

const carrierIds = [
  "mars-deferent-e",
  "mercury-deferent-a",
  "venus-deferent-a",
  "eros-deferent-a",
];

let failed = false;
console.log("Full binary direct-settings migration audit\n");
carrierIds.forEach((carrierId) => {
  const direct = current.get(carrierId);
  let maximumCentreError = 0;
  let maximumAnnualError = 0;

  for (let index = 0; index <= 4096; index += 1) {
    const position = -100 + (200 * index) / 4096;
    const expected = legacyRelative(carrierId, position);
    const actual = directRelative(direct, position);
    maximumCentreError = Math.max(
      maximumCentreError,
      expected.centre.distanceTo(actual.centre)
    );
    maximumAnnualError = Math.max(
      maximumAnnualError,
      expected.annual.distanceTo(actual.annual)
    );
  }

  const valid =
    number(direct, "orbitRadius") === 0 &&
    maximumCentreError < 1e-12 &&
    maximumAnnualError < 1e-10;
  failed ||= !valid;
  console.log(
    `${carrierId}: ${valid ? "PASS" : "FAIL"}; ` +
      `centre error=${maximumCentreError}; annual error=${maximumAnnualError}`
  );
});

if (failed) process.exitCode = 1;
