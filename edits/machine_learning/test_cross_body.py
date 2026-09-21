"""Tests for multi-coordinate and cross-body scientific invariants."""

import unittest

import numpy as np

import cross_body


class CrossBodyTests(unittest.TestCase):
    def test_ridge_does_not_penalize_intercept(self):
        x = np.column_stack((np.ones(20), np.linspace(-1, 1, 20)))
        y = np.column_stack((np.full(20, 3.0), np.full(20, -2.0)))
        coefficients = cross_body.ridge_fit(x, y, 1000.0)
        np.testing.assert_allclose(coefficients[0], [3.0, -2.0], atol=1e-12)
        np.testing.assert_allclose(coefficients[1], [0.0, 0.0], atol=1e-12)

    def test_global_rotation_preserves_pairwise_separation(self):
        first = cross_body.unit_vectors(np.array([10.0, 20.0]), np.array([5.0, -4.0]))
        second = cross_body.unit_vectors(np.array([70.0, 80.0]), np.array([-3.0, 8.0]))
        angle = np.radians(31.0)
        rotation = np.array(((np.cos(angle), -np.sin(angle), 0.0),
                             (np.sin(angle), np.cos(angle), 0.0),
                             (0.0, 0.0, 1.0)))
        before = cross_body.angular_separation(first, second)
        after = cross_body.angular_separation(first @ rotation.T, second @ rotation.T)
        np.testing.assert_allclose(before, after, atol=1e-12)

    def test_tangent_metric_uses_both_coordinates(self):
        residuals = np.zeros((2, 4))
        residuals[:, 2] = [3.0, 0.0]
        residuals[:, 3] = [4.0, 0.0]
        self.assertAlmostEqual(cross_body.combined_tangent_rmse(residuals),
                               np.sqrt(12.5))


if __name__ == "__main__":
    unittest.main()
