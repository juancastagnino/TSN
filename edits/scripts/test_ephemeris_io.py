import unittest

from ephemeris_io import tychos_metadata, validate_tychos_j2000_header


class TychosReferenceFrameMetadataTests(unittest.TestCase):
    def test_accepts_explicit_j2000_export(self):
        text = "\n".join(
            (
                "--- EPHEMERIDES REPORT ---",
                "Reference frame: J2000 / ICRF comparison",
                "Coordinates: geometric (no light-time or aberration)",
                "PLANET: SUN",
            )
        )

        metadata = validate_tychos_j2000_header(text)

        self.assertEqual(metadata["reference_frame"], "j2000-icrf")
        self.assertEqual(
            metadata["coordinates"], "geometric (no light-time or aberration)"
        )

    def test_rejects_native_export_for_icrf_comparison(self):
        text = "Reference frame: TYCHOS native (moving PVP)\nPLANET: SUN"

        with self.assertRaisesRegex(ValueError, "moving native/PVP frame"):
            validate_tychos_j2000_header(text)

    def test_accepts_native_export_only_with_explicit_opt_in(self):
        text = "Reference frame: TYCHOS native (moving PVP)\nPLANET: SUN"

        metadata = validate_tychos_j2000_header(text, allow_native=True)

        self.assertEqual(metadata["reference_frame"], "tychos-native")

    def test_rejects_unlabelled_legacy_export(self):
        text = "PLANET: SUN"

        self.assertIsNone(tychos_metadata(text)["reference_frame"])
        with self.assertRaisesRegex(ValueError, "does not declare"):
            validate_tychos_j2000_header(text)


if __name__ == "__main__":
    unittest.main()
