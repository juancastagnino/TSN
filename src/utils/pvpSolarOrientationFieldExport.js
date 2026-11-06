import { Quaternion, Vector3 } from "three";
import {
  declinationToRadians,
  rightAscensionToRadians,
  sphericalToCartesian,
} from "./celestial-functions";
import { dateTimeToPos } from "./time-date-functions";
import { getPvpSolarOrientationQuaternion } from "../components/PvpSolarOrientationFrame";

// These directions are deliberately spread around the sky.  They are modern
// catalogue-style directions used to map the model's predicted field pattern;
// they are not substituted for historical 1856 astrometry.
export const PVP_ORIENTATION_FIELD_STARS = [
  { name: "Gamma Draconis", ra: "17h 56m 36.4s", dec: "+51° 29' 20\"" },
  { name: "Sirius", ra: "06h 45m 08.9s", dec: "-16° 42' 58\"" },
  { name: "Vega", ra: "18h 36m 56.3s", dec: "+38° 47' 01\"" },
  { name: "Arcturus", ra: "14h 15m 39.7s", dec: "+19° 10' 56\"" },
  { name: "Capella", ra: "05h 16m 41.4s", dec: "+45° 59' 53\"" },
  { name: "Polaris", ra: "02h 31m 49.1s", dec: "+89° 15' 51\"" },
  { name: "Altair", ra: "19h 50m 47.0s", dec: "+08° 52' 06\"" },
  { name: "Barnard's Star", ra: "17h 57m 47.1s", dec: "+04° 41' 34\"" },
];

export const GREENWICH_1856_FIELD_DATES = [
  { label: "1856-01-02", date: "1856-01-02", time: "11:08:05" },
  { label: "1856-08-12", date: "1856-08-12", time: "20:27:25" },
  { label: "1856-09-05", date: "1856-09-05", time: "18:53:03" },
  { label: "1856-12-11", date: "1856-12-11", time: "12:31:37" },
  { label: "1856-12-20", date: "1856-12-20", time: "12:00:10" },
];

const R2A = (180 / Math.PI) * 3600;
const wrapRadians = (value) => Math.atan2(Math.sin(value), Math.cos(value));

const directionFromRaDec = (ra, dec, target = new Vector3()) => {
  const position = sphericalToCartesian(
    rightAscensionToRadians(ra),
    declinationToRadians(dec),
    1
  );
  return target.set(position.x, position.y, position.z).normalize();
};

const raDecFromDirection = (direction) => ({
  ra: Math.atan2(direction.x, direction.z),
  dec: Math.asin(Math.max(-1, Math.min(1, direction.y))),
});

export const buildPvpSolarOrientationFieldRows = ({ sun, amplitudeArcsec }) => {
  const quaternion = new Quaternion();
  const current = new Vector3();
  const reference = new Vector3();
  const axis = new Vector3();
  const baseline = new Vector3();
  const shifted = new Vector3();

  return GREENWICH_1856_FIELD_DATES.flatMap(({ label, date, time }) => {
    const position = dateTimeToPos(date, time);
    getPvpSolarOrientationQuaternion(
      sun,
      position,
      amplitudeArcsec,
      quaternion,
      current,
      reference,
      axis
    );
    // Fixed stellar directions are seen through the inverse of the system
    // frame rotation, whereas planets and Earth share the frame itself.
    const apparentStarQuaternion = quaternion.clone().invert();
    const frameRotationArcsec = 2 * Math.acos(Math.min(1, Math.abs(quaternion.w))) * R2A;

    return PVP_ORIENTATION_FIELD_STARS.map((star) => {
      directionFromRaDec(star.ra, star.dec, baseline);
      shifted.copy(baseline).applyQuaternion(apparentStarQuaternion);
      const before = raDecFromDirection(baseline);
      const after = raDecFromDirection(shifted);
      const raCoordinateDelta = wrapRadians(after.ra - before.ra) * R2A;
      const decDelta = (after.dec - before.dec) * R2A;
      const tangentEastDelta = raCoordinateDelta * Math.cos(before.dec);
      const totalShift = Math.acos(
        Math.max(-1, Math.min(1, baseline.dot(shifted)))
      ) * R2A;

      return {
        date: label,
        time_utc: time,
        star: star.name,
        catalog_ra: star.ra,
        catalog_dec: star.dec,
        amplitude_arcsec: Number(amplitudeArcsec),
        frame_rotation_arcsec: frameRotationArcsec,
        delta_ra_coordinate_arcsec: raCoordinateDelta,
        delta_ra_tangent_east_arcsec: tangentEastDelta,
        delta_dec_arcsec: decDelta,
        total_sky_shift_arcsec: totalShift,
      };
    });
  });
};

const csvEscape = (value) => `"${String(value).replaceAll('"', '""')}"`;

export const downloadPvpSolarOrientationFieldCsv = ({
  sun,
  amplitudeArcsec,
  filename,
}) => {
  const rows = buildPvpSolarOrientationFieldRows({ sun, amplitudeArcsec });
  const headings = Object.keys(rows[0] || {});
  const csv = [
    headings.join(","),
    ...rows.map((row) => headings.map((heading) => csvEscape(row[heading])).join(",")),
  ].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const suffix =
    filename ||
    (Number(amplitudeArcsec) === 0
      ? "zero"
      : String(amplitudeArcsec).replace(/[^0-9-]/g, ""));
  link.download = `tychos_pvp_solar_orientation_field_1856_${suffix}.csv`;
  link.click();
  URL.revokeObjectURL(url);
  return rows;
};
