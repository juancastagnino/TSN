import { EPHEMERIS_REFERENCE_FRAMES } from "../../utils/plotModelFunctions";
import { parseEphemerisReferenceFrame } from "./checkerStore";

test("detects J2000/ICRF ephemeris reports", () => {
  const text = [
    "--- EPHEMERIDES REPORT ---",
    "Reference frame: J2000 / ICRF comparison",
    "PLANET: SUN",
  ].join("\n");

  expect(parseEphemerisReferenceFrame(text)).toBe(
    EPHEMERIS_REFERENCE_FRAMES.J2000_ICRF
  );
});

test("treats legacy and native reports as TYCHOS native", () => {
  expect(parseEphemerisReferenceFrame("PLANET: SUN")).toBe(
    EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE
  );
  expect(
    parseEphemerisReferenceFrame("Reference frame: TYCHOS native (moving PVP)")
  ).toBe(EPHEMERIS_REFERENCE_FRAMES.TYCHOS_NATIVE);
});
