import unittest

from secular_equilibrium import calculate_secular_equilibrium


class TestSecularEquilibrium(unittest.TestCase):

    def test_u238_chain(self):
        """Test U-238 decay chain calculation."""
        results = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False,
        )

        self.assertAlmostEqual(
            results['U-238']['activity_Bq'] * results['U-238']['branching_ratio'],
            100.0,
            places=5,
        )
        self.assertGreater(results['U-238']['mass_g'], 0)

    def test_invalid_nuclide(self):
        """Test invalid nuclide name."""
        with self.assertRaises(ValueError):
            calculate_secular_equilibrium(
                measured_nuclide='Invalid-999',
                measured_activity=100.0,
                parent_nuclides=['U-238'],
                verbose=False,
            )

    def test_decay_type_parameter(self):
        """Test decay_type parameter functionality."""
        results = calculate_secular_equilibrium(
            measured_nuclide='U-238',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            decay_type='α',
            verbose=False,
        )

        self.assertIn('U-238', results)
        self.assertGreater(results['U-238']['mass_g'], 0)

        results_shorthand = calculate_secular_equilibrium(
            measured_nuclide='U-238',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            decay_type='a',
            verbose=False,
        )

        self.assertAlmostEqual(
            results['U-238']['activity_Bq'],
            results_shorthand['U-238']['activity_Bq'],
            places=10,
        )

    def test_invalid_decay_type(self):
        """Test invalid decay type."""
        with self.assertRaises(ValueError):
            calculate_secular_equilibrium(
                measured_nuclide='Pb-214',
                measured_activity=100.0,
                parent_nuclides=['U-238'],
                decay_type='invalid',
                verbose=False,
            )

    def test_decay_type_adjustment(self):
        """Test that decay type adjusts measured activity correctly."""
        import radioactivedecay as rd

        pb214 = rd.Nuclide('Pb-214')
        modes = pb214.decay_modes()
        fractions = pb214.branching_fractions()

        beta_fraction = 0.0
        for mode, fraction in zip(modes, fractions):
            if 'β-' in mode:
                beta_fraction += fraction

        self.assertGreater(beta_fraction, 0.99)

        results_with_decay = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            decay_type='β-',
            verbose=False,
        )

        results_without_decay = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False,
        )

        self.assertAlmostEqual(
            results_with_decay['U-238']['activity_Bq'],
            results_without_decay['U-238']['activity_Bq'],
            places=5,
        )

    def test_uncertainty_propagation(self):
        """Test uncertainty propagation from measured activity to parent results."""
        results = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            measured_activity_uncertainty=5.0,
            parent_nuclides=['U-238'],
            verbose=False,
        )

        data = results['U-238']
        self.assertAlmostEqual(
            data['activity_uncertainty_Bq'] * data['branching_ratio'],
            5.0,
            places=5,
        )
        self.assertAlmostEqual(data['relative_uncertainty'], 0.05, places=10)
        self.assertAlmostEqual(
            data['mass_uncertainty_g'] / data['mass_g'],
            0.05,
            places=10,
        )

    def test_invalid_uncertainty(self):
        """Test invalid uncertainty value."""
        with self.assertRaises(ValueError):
            calculate_secular_equilibrium(
                measured_nuclide='Pb-214',
                measured_activity=100.0,
                measured_activity_uncertainty=-1.0,
                parent_nuclides=['U-238'],
                verbose=False,
            )

    def test_include_paths_consistency_with_multiple_paths(self):
        """Test multi-path decomposition sums to total branching ratio."""
        results = calculate_secular_equilibrium(
            measured_nuclide='Ra-223',
            measured_activity=100.0,
            parent_nuclides=['Ac-227'],
            include_paths=True,
            verbose=False,
        )

        data = results['Ac-227']
        paths = data.get('paths', [])

        self.assertGreater(len(paths), 1)
        total_from_paths = sum(path['path_branching_ratio'] for path in paths)
        self.assertAlmostEqual(total_from_paths, data['branching_ratio'], places=12)

    def test_paths_not_returned_by_default(self):
        """Test that path details are omitted unless explicitly requested."""
        results = calculate_secular_equilibrium(
            measured_nuclide='Pb-214',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False,
        )
        self.assertNotIn('paths', results['U-238'])


if __name__ == '__main__':
    unittest.main()
