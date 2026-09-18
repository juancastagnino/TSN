"""Scientific invariants: held-out labels cannot affect the fit or selection."""
import contextlib
import io
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np
import run


class ExperimentTests(unittest.TestCase):
    def fixture(self):
        config = {
            'tychos': 'edits/data/raw/tychos_ephemerides.txt',
            'jpl': 'edits/data/raw/jpl_ephemerides.txt',
            'start': '2000-01-01', 'validation_start': '2000-03-01',
            'test_start': '2000-05-01', 'stop_exclusive': '2000-07-01',
            'cadence_hours': 24, 'periods_days': [14.765294],
        }
        dates = [datetime(2000, 1, 1)+timedelta(days=i) for i in range(182)]
        ty = {d: {'ra': 100 + np.sin(i), 'dec': 5} for i, d in enumerate(dates)}
        jp = {d: {'ra_icrf': 100, 'dec_icrf': 5} for d in dates}
        return config, ty, jp

    def execute(self, config, ty, jp):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(run, 'read_tychos', return_value=ty), \
                patch.object(run, 'read_jpl', return_value=jp), \
                contextlib.redirect_stdout(io.StringIO()):
            return run.run(config, Path(directory))

    def test_test_labels_do_not_affect_training_or_selection(self):
        config, ty, jp = self.fixture()
        first = self.execute(config, ty, jp)
        for date in jp:
            if date >= datetime(2000, 5, 1):
                jp[date]['ra_icrf'] += 10
        second = self.execute(config, ty, jp)
        self.assertEqual(first['candidates'], second['candidates'])
        self.assertEqual(first['selected'], second['selected'])
        self.assertNotEqual(first['test'], second['test'])

    def test_mismatched_grid_rejected(self):
        config, ty, jp = self.fixture()
        del jp[next(iter(jp))]
        with self.assertRaisesRegex(ValueError, 'identical'):
            self.execute(config, ty, jp)

    def test_non_lunar_identity_is_preserved(self):
        config, ty, jp = self.fixture()
        config['body'] = 'mars'
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(run, 'read_tychos', return_value=ty) as read_ty, \
                patch.object(run, 'read_jpl', return_value=jp) as read_jp, \
                contextlib.redirect_stdout(io.StringIO()):
            result = run.run(config, Path(directory))
            self.assertEqual(result['body'], 'mars')
            self.assertEqual(read_ty.call_args.kwargs['body'], 'mars')
            self.assertEqual(read_jp.call_args.kwargs['target_id'], '499')
            self.assertIn(',mars,', (Path(directory)/'dataset.csv').read_text())

    def test_missing_body_requires_explicit_partial_run(self):
        config, _, _ = self.fixture()
        config['bodies'] = ['moon', 'venus']
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(run, 'tychos_blocks', return_value={'moon': ''}), \
                patch.object(run, 'jpl_blocks', return_value={'301': ''}), \
                patch.object(run, 'run') as fit:
            with self.assertRaisesRegex(ValueError, 'Missing exports'):
                run.run_all(config, Path(directory))
            fit.assert_not_called()

    def test_shared_gap_rejected(self):
        config, ty, jp = self.fixture()
        date = datetime(2000, 2, 1)
        del ty[date]
        del jp[date]
        with self.assertRaisesRegex(ValueError, 'irregular'):
            self.execute(config, ty, jp)

    def test_split_boundaries_and_fixed_time_origin(self):
        config, _, _ = self.fixture()
        dates = [datetime(2000, 2, 29), datetime(2000, 3, 1), datetime(2000, 5, 1)]
        self.assertEqual(run.split_dates(dates, config).tolist(), ['train', 'validation', 'test'])
        t = np.arange(100.)
        whole, _ = run.design(t, [14.765294], True, 20.)
        future, _ = run.design(t[70:], [14.765294], True, 20.)
        np.testing.assert_array_equal(whole[70:], future)


if __name__ == '__main__':
    unittest.main()
