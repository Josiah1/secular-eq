import unittest
from secular_equilibrium import calculate_secular_equilibrium

class TestSecularEquilibrium(unittest.TestCase):

    def test_u238_chain(self):
        """Test U-238 decay chain calculation"""
        results = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False
        )

        # Check that U-238 activity should equal measured activity (considering branching ratio)
        self.assertAlmostEqual(
            results['U-238']['activity_Bq'] * results['U-238']['branching_ratio'],
            100.0,
            places=5
        )

        # Check mass is positive
        self.assertGreater(results['U-238']['mass_g'], 0)

    def test_invalid_nuclide(self):
        """Test invalid nuclide name"""
        with self.assertRaises(ValueError):
            calculate_secular_equilibrium(
                measured_nuclide='Invalid-999',
                measured_activity=100.0,
                parent_nuclides=['U-238'],
                verbose=False
            )

    def test_decay_type_parameter(self):
        """Test decay_type parameter functionality"""
        # Test with a nuclide that has alpha decay (U-238 itself)
        results = calculate_secular_equilibrium(
            measured_nuclide='U-238',
            measured_activity=100.0,
            parent_nuclides=['U-238'],  # Same nuclide for simple test
            decay_type='α',
            verbose=False
        )

        # Basic validation that calculation completes
        self.assertIn('U-238', results)
        self.assertGreater(results['U-238']['mass_g'], 0)

        # Test with shorthand 'a' for alpha
        results_shorthand = calculate_secular_equilibrium(
            measured_nuclide='U-238',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            decay_type='a',
            verbose=False
        )

        # Results should be the same (within floating point precision)
        self.assertAlmostEqual(
            results['U-238']['activity_Bq'],
            results_shorthand['U-238']['activity_Bq'],
            places=10
        )

    def test_invalid_decay_type(self):
        """Test invalid decay type"""
        with self.assertRaises(ValueError):
            calculate_secular_equilibrium(
                measured_nuclide='Pb-214',
                measured_activity=100.0,
                parent_nuclides=['U-238'],
                decay_type='invalid',
                verbose=False
            )

    def test_decay_type_adjustment(self):
        """Test that decay type adjusts measured activity correctly"""
        # This test verifies that when decay_type is specified,
        # the measured activity is adjusted for the decay branching ratio
        # We'll test with a nuclide that has known branching ratios
        import radioactivedecay as rd

        # Get Pb-214 decay modes and fractions
        pb214 = rd.Nuclide('Pb-214')
        modes = pb214.decay_modes()
        fractions = pb214.branching_fractions()

        # Find beta- decay fraction (Pb-214 decays via β- to Bi-214)
        beta_fraction = 0.0
        for mode, fraction in zip(modes, fractions):
            if 'β-' in mode:
                beta_fraction += fraction

        # Should be close to 1.0 for Pb-214
        self.assertGreater(beta_fraction, 0.99)

        # Test calculation with and without decay type specification
        # Since Pb-214 decays almost exclusively via β-, results should be similar
        results_with_decay = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            decay_type='β-',
            verbose=False
        )

        results_without_decay = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False
        )

        # Since branching ratio is ~1.0, results should be very similar
        self.assertAlmostEqual(
            results_with_decay['U-238']['activity_Bq'],
            results_without_decay['U-238']['activity_Bq'],
            places=5
        )

if __name__ == '__main__':
    unittest.main()