import json
import tempfile
import unittest
from pathlib import Path

from dataset import read_export


class ExportValidationTests(unittest.TestCase):
    def fixture(self):
        dates = ['2000-06-21T00:00:00', '2000-06-21T06:00:00']
        manifest = {'dates': dates, 'bodies': ['moon'], 'run_id': 'test'}
        entries = [{'kind': 'metadata', 'source': 'Stellarium', 'run_id': 'test', 'planetocentric': True,
                    'light_travel_time': False, 'aberration': False}]
        for i, date in enumerate(dates):
            entries.append({'kind': 'position', 'date': date, 'actual_date': date,
                            'body': 'moon', 'ra': 317+i*3, 'dec': -18+i,
                            'ra_date': 317+i*3, 'dec_date': -18+i, 'delta_t_seconds': 64})
        entries.append({'kind': 'complete', 'count': 2})
        return manifest, entries

    def read(self, manifest, entries):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'export.jsonl'
            path.write_text('\n'.join(json.dumps(x) for x in entries))
            return read_export(path, manifest)

    def test_complete_export(self):
        manifest, entries = self.fixture()
        self.assertEqual(len(self.read(manifest, entries)[1]), 2)

    def test_missing_completion(self):
        manifest, entries = self.fixture()
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            self.read(manifest, entries[:-1])

    def test_wrong_date(self):
        manifest, entries = self.fixture()
        entries[2]['actual_date'] = entries[1]['actual_date']
        with self.assertRaisesRegex(ValueError, 'date'):
            self.read(manifest, entries)

    def test_stale_positions(self):
        manifest, entries = self.fixture()
        entries[2]['ra'], entries[2]['dec'] = entries[1]['ra'], entries[1]['dec']
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            self.read(manifest, entries)

    def test_wrong_observer(self):
        manifest, entries = self.fixture()
        entries[0]['planetocentric'] = False
        with self.assertRaisesRegex(ValueError, 'settings'):
            self.read(manifest, entries)

    def test_previous_export_rejected(self):
        manifest, entries = self.fixture()
        entries[0]['run_id'] = 'previous'
        with self.assertRaisesRegex(ValueError, 'earlier run'):
            self.read(manifest, entries)


if __name__ == '__main__':
    unittest.main()
