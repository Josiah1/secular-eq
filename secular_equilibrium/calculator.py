"""
Secular Equilibrium Calculator for Radioactive Decay Chains.

This package calculates parent nuclide activities and masses from measured
progeny activities, assuming secular equilibrium conditions.
"""

import math
from typing import Dict, List, Optional

import radioactivedecay as rd


class SecularEquilibriumCalculator:
    """
    Secular equilibrium calculator for radioactive decay chains.

    Attributes:
        measured_nuclide: Measured nuclide name (e.g., 'Pb-214')
        measured_activity: Measured activity (Bq)
        parent_nuclides: List of parent nuclides to consider (e.g., ['U-238', 'Ra-226'])
    """

    VALID_DECAY_TYPES = ['α', 'β-', 'β+', 'EC', 'SF', 'IT', 'p', 'n', 'd', 't']
    MAX_DEPTH = 30

    @staticmethod
    def _normalize_decay_type(decay_type: Optional[str]) -> Optional[str]:
        """
        Normalize decay type shorthand to standard notation.

        Supported shorthands:
        - 'a', 'alpha' -> 'α'
        - 'b', 'b-', 'beta', 'beta-' -> 'β-'
        - 'b+', 'beta+' -> 'β+'
        - 'e', 'ec' -> 'EC'

        Args:
            decay_type: Input decay type string or shorthand

        Returns:
            Normalized decay type string or None
        """
        if decay_type is None:
            return None

        decay_type = decay_type.strip()
        if decay_type in SecularEquilibriumCalculator.VALID_DECAY_TYPES:
            return decay_type

        decay_type_lower = decay_type.lower()
        decay_type_map = {
            'a': 'α',
            'alpha': 'α',
            'b': 'β-',
            'b-': 'β-',
            'beta': 'β-',
            'beta-': 'β-',
            'b+': 'β+',
            'beta+': 'β+',
            'e': 'EC',
            'ec': 'EC',
        }

        return decay_type_map.get(decay_type_lower, decay_type)

    def __init__(
        self,
        measured_nuclide: str,
        measured_activity: float,
        parent_nuclides: List[str],
        decay_type: Optional[str] = None,
        measured_activity_uncertainty: Optional[float] = None,
        include_paths: bool = False,
    ):
        """
        Initialize the calculator.

        Args:
            measured_nuclide: Measured nuclide name (e.g., 'Pb-214', 'Bi-214')
            measured_activity: Measured activity (Bq)
            parent_nuclides: List of parent nuclides (e.g., ['U-238', 'Th-232'])
            decay_type: Optional decay type to consider (e.g., 'α', 'β-', 'β+', 'EC').
                       If None, considers all decay types (default).
            measured_activity_uncertainty: Optional uncertainty (1-sigma) of measured activity (Bq).
            include_paths: If True, include path-level branching details in output.
        """
        self.measured_nuclide = measured_nuclide
        self.measured_activity = measured_activity
        self.parent_nuclides = parent_nuclides
        self.decay_type = self._normalize_decay_type(decay_type)
        self.measured_activity_uncertainty = measured_activity_uncertainty
        self.include_paths = include_paths
        self._branching_cache = {}
        self._decay_fraction_cache = {}

        self._validate_nuclides()

    def _validate_nuclides(self):
        """Validate that nuclide names, decay type, and uncertainty are valid."""
        try:
            rd.Nuclide(self.measured_nuclide)
        except Exception:
            raise ValueError("Invalid measured nuclide name: {0}".format(self.measured_nuclide))

        for parent in self.parent_nuclides:
            try:
                rd.Nuclide(parent)
            except Exception:
                raise ValueError("Invalid parent nuclide name: {0}".format(parent))

        if self.decay_type is not None:
            if not isinstance(self.decay_type, str) or self.decay_type.strip() == '':
                raise ValueError("Invalid decay type: {0}. Must be a non-empty string.".format(self.decay_type))
            if self.decay_type not in self.VALID_DECAY_TYPES:
                raise ValueError(
                    "Invalid decay type: {0}. Valid types: {1}".format(
                        self.decay_type,
                        ', '.join(self.VALID_DECAY_TYPES),
                    )
                )

        if self.measured_activity_uncertainty is not None:
            if self.measured_activity_uncertainty < 0:
                raise ValueError("measured_activity_uncertainty must be >= 0")

    @staticmethod
    def _is_nuclide_name(name: str) -> bool:
        """Return True when the given decay child token is a nuclide name."""
        try:
            rd.Nuclide(name)
            return True
        except Exception:
            return False

    def _get_decay_fraction_for_nuclide(self, nuclide: str) -> float:
        """
        Get the branching fraction of the measured nuclide for self.decay_type.

        If no decay_type filter is provided, returns 1.0.
        """
        if self.decay_type is None:
            return 1.0

        cache_key = (nuclide, self.decay_type)
        if cache_key in self._decay_fraction_cache:
            return self._decay_fraction_cache[cache_key]

        target_nuclide = rd.Nuclide(nuclide)
        modes = target_nuclide.decay_modes()
        fractions = target_nuclide.branching_fractions()

        matching_fraction = 0.0
        for mode, fraction in zip(modes, fractions):
            if self.decay_type in mode:
                matching_fraction += fraction

        self._decay_fraction_cache[cache_key] = matching_fraction
        return matching_fraction

    def _enumerate_chain_paths(self, parent: str, progeny: str) -> List[Dict[str, object]]:
        """
        Enumerate all acyclic decay paths from parent to progeny.

        Returns path entries with chain-level branching ratios (without measured-decay-type weighting).
        """
        if parent == progeny:
            return [{
                'nodes': [parent],
                'decay_modes': [],
                'step_branching_fractions': [],
                'chain_branching_ratio': 1.0,
            }]

        paths = []

        def dfs(
            current: str,
            visited: set,
            nodes: List[str],
            modes: List[str],
            step_fractions: List[float],
            cumulative_ratio: float,
            depth: int,
        ):
            if depth > self.MAX_DEPTH:
                return

            if current == progeny:
                paths.append({
                    'nodes': nodes,
                    'decay_modes': modes,
                    'step_branching_fractions': step_fractions,
                    'chain_branching_ratio': cumulative_ratio,
                })
                return

            try:
                nuclide = rd.Nuclide(current)
            except Exception:
                return

            child_modes = nuclide.decay_modes()
            child_fractions = nuclide.branching_fractions()
            child_nuclides = nuclide.progeny()

            for mode, fraction, child in zip(child_modes, child_fractions, child_nuclides):
                if not self._is_nuclide_name(child):
                    continue
                if child in visited:
                    continue
                dfs(
                    child,
                    visited | {child},
                    nodes + [child],
                    modes + [mode],
                    step_fractions + [fraction],
                    cumulative_ratio * fraction,
                    depth + 1,
                )

        dfs(parent, {parent}, [parent], [], [], 1.0, 0)
        return paths

    def _get_branching_info(self, parent: str, progeny: str) -> Dict[str, object]:
        """
        Calculate cumulative branching ratio and per-path contributions.

        Returns:
            {
                'branching_ratio': float,
                'paths': List[path_dict],
                'decay_type_fraction_at_measured': float
            }
        """
        cache_key = (parent, progeny, self.decay_type)
        if cache_key in self._branching_cache:
            return self._branching_cache[cache_key]

        try:
            progeny_nuclide = rd.Nuclide(progeny)
        except Exception:
            raise ValueError("Invalid progeny nuclide name: {0}".format(progeny))

        progeny_halflife = progeny_nuclide.half_life('s')
        if progeny_halflife == float('inf'):
            raise ValueError("{0} is a stable nuclide and cannot establish secular equilibrium".format(progeny))

        chain_paths = self._enumerate_chain_paths(parent, progeny)
        if not chain_paths:
            raise ValueError("{0} is not in {1}'s decay chain".format(progeny, parent))

        # Keep historical behavior: if parent == measured nuclide, ratio remains 1 even when decay_type is set.
        if self.decay_type is not None and parent != progeny:
            decay_type_fraction = self._get_decay_fraction_for_nuclide(progeny)
        else:
            decay_type_fraction = 1.0

        path_details = []
        total_branching_ratio = 0.0
        for path in chain_paths:
            path_ratio = path['chain_branching_ratio'] * decay_type_fraction
            details = {
                'nodes': path['nodes'],
                'decay_modes': path['decay_modes'],
                'step_branching_fractions': path['step_branching_fractions'],
                'chain_branching_ratio': path['chain_branching_ratio'],
                'decay_type_fraction_at_measured': decay_type_fraction,
                'path_branching_ratio': path_ratio,
            }
            total_branching_ratio += path_ratio
            path_details.append(details)

        if total_branching_ratio < 1e-15:
            raise ValueError("{0} is not in {1}'s decay chain".format(progeny, parent))

        path_details.sort(key=lambda item: item['path_branching_ratio'], reverse=True)

        info = {
            'branching_ratio': total_branching_ratio,
            'paths': path_details,
            'decay_type_fraction_at_measured': decay_type_fraction,
        }
        self._branching_cache[cache_key] = info
        return info

    def _get_branching_ratio(self, parent: str, progeny: str) -> float:
        """Backwards-compatible helper returning only cumulative branching ratio."""
        info = self._get_branching_info(parent, progeny)
        return info['branching_ratio']

    def calculate(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate activities and masses for parent nuclides.

        Returns:
            Dictionary with format:
            {
                'parent_name': {
                    'activity_Bq': float,
                    'mass_g': float,
                    'branching_ratio': float,
                    'halflife_yr': float,
                    'atomic_mass': float,
                    ... optional uncertainty/path fields ...
                }
            }
        """
        results = {}
        avogadro_number = 6.02214076e23

        for parent in self.parent_nuclides:
            try:
                branching_info = self._get_branching_info(parent, self.measured_nuclide)
                branching_ratio = branching_info['branching_ratio']
            except ValueError as exc:
                result = {
                    'activity_Bq': 0.0,
                    'mass_g': 0.0,
                    'branching_ratio': 0.0,
                    'halflife_yr': 0.0,
                    'error': str(exc),
                }
                if self.include_paths:
                    result['paths'] = []
                    result['total_branching_ratio'] = 0.0
                results[parent] = result
                continue

            parent_activity = self.measured_activity / branching_ratio

            parent_nuclide = rd.Nuclide(parent)
            parent_halflife_s = parent_nuclide.half_life('s')
            parent_halflife_yr = parent_halflife_s / (365.25 * 24 * 3600)
            parent_mass_amu = parent_nuclide.atomic_mass

            if parent_halflife_s == float('inf'):
                parent_mass = float('inf')
                mass_coefficient = None
            else:
                lambda_parent = math.log(2) / parent_halflife_s
                mass_coefficient = parent_mass_amu / (avogadro_number * lambda_parent)
                parent_mass = parent_activity * mass_coefficient

            result = {
                'activity_Bq': parent_activity,
                'mass_g': parent_mass,
                'branching_ratio': branching_ratio,
                'halflife_yr': parent_halflife_yr,
                'atomic_mass': parent_mass_amu,
            }

            if self.measured_activity_uncertainty is not None:
                activity_uncertainty = self.measured_activity_uncertainty / branching_ratio
                if parent_halflife_s == float('inf'):
                    mass_uncertainty = float('inf')
                else:
                    mass_uncertainty = activity_uncertainty * mass_coefficient

                if parent_activity == 0.0:
                    relative_uncertainty = None
                else:
                    relative_uncertainty = activity_uncertainty / abs(parent_activity)

                result['activity_uncertainty_Bq'] = activity_uncertainty
                result['mass_uncertainty_g'] = mass_uncertainty
                result['relative_uncertainty'] = relative_uncertainty

            if self.include_paths:
                result['paths'] = branching_info['paths']
                result['total_branching_ratio'] = branching_ratio

            results[parent] = result

        return results

    def print_results(self, results: Optional[Dict] = None):
        """
        Print calculation results.

        Args:
            results: Calculation results dictionary (if None, recalculate)
        """
        if results is None:
            results = self.calculate()

        print("=" * 80)
        print("Secular Equilibrium Calculation Results")
        print("=" * 80)
        print("\nMeasured nuclide: {0}".format(self.measured_nuclide))
        print("Measured activity: {0:.4e} Bq".format(self.measured_activity))
        if self.measured_activity_uncertainty is not None:
            print("Measured activity uncertainty: {0:.4e} Bq".format(self.measured_activity_uncertainty))
        print("\n" + "-" * 80)

        for parent, data in results.items():
            print("\nParent nuclide: {0}".format(parent))

            if 'error' in data:
                print("  Error: {0}".format(data['error']))
                print(
                    "  Branching ratio ({0} -> {1}): {2:.6f}".format(
                        parent,
                        self.measured_nuclide,
                        data['branching_ratio'],
                    )
                )
                continue

            print("  Half-life: {0:.4e} years".format(data['halflife_yr']))
            print("  Atomic mass: {0:.4f} u".format(data['atomic_mass']))
            print(
                "  Branching ratio ({0} -> {1}): {2:.6f}".format(
                    parent,
                    self.measured_nuclide,
                    data['branching_ratio'],
                )
            )
            print("  Calculated activity: {0:.4e} Bq".format(data['activity_Bq']))

            if data['mass_g'] == float('inf'):
                print("  Mass: Cannot calculate (stable nuclide)")
            else:
                print("  Mass: {0:.4e} g".format(data['mass_g']))
                if data['mass_g'] < 1e-6:
                    print("       {0:.4e} ng".format(data['mass_g'] * 1e9))
                elif data['mass_g'] < 1e-3:
                    print("       {0:.4e} ug".format(data['mass_g'] * 1e6))
                elif data['mass_g'] < 1:
                    print("       {0:.4e} mg".format(data['mass_g'] * 1e3))

            if 'activity_uncertainty_Bq' in data:
                print("  Activity uncertainty: {0:.4e} Bq".format(data['activity_uncertainty_Bq']))
                if data['mass_uncertainty_g'] == float('inf'):
                    print("  Mass uncertainty: inf")
                else:
                    print("  Mass uncertainty: {0:.4e} g".format(data['mass_uncertainty_g']))
                if data['relative_uncertainty'] is None:
                    print("  Relative uncertainty: N/A (zero activity)")
                else:
                    print("  Relative uncertainty: {0:.2%}".format(data['relative_uncertainty']))

            if self.include_paths:
                print("  Path contributions:")
                paths = data.get('paths', [])
                if not paths:
                    print("    (none)")
                for idx, path in enumerate(paths, start=1):
                    path_nodes = " -> ".join(path['nodes'])
                    path_modes = " | ".join(path['decay_modes']) if path['decay_modes'] else "(same nuclide)"
                    print("    [{0}] {1}".format(idx, path_nodes))
                    print("        Modes: {0}".format(path_modes))
                    print("        Chain branching ratio: {0:.6e}".format(path['chain_branching_ratio']))
                    if self.decay_type is not None and path['decay_type_fraction_at_measured'] != 1.0:
                        print(
                            "        Measured decay-type fraction ({0}): {1:.6e}".format(
                                self.decay_type,
                                path['decay_type_fraction_at_measured'],
                            )
                        )
                    print("        Path contribution: {0:.6e}".format(path['path_branching_ratio']))

        print("\n" + "=" * 80)


def calculate_secular_equilibrium(
    measured_nuclide: str,
    measured_activity: float,
    parent_nuclides: List[str],
    decay_type: Optional[str] = None,
    verbose: bool = True,
    measured_activity_uncertainty: Optional[float] = None,
    include_paths: bool = False,
) -> Dict[str, Dict[str, float]]:
    """
    Convenience function: calculate secular equilibrium for radioactive decay chains.

    Args:
        measured_nuclide: Measured nuclide name (e.g., 'Pb-214')
        measured_activity: Measured activity (Bq)
        parent_nuclides: Parent nuclides list (e.g., ['U-238', 'Ra-226'])
        decay_type: Optional decay type to consider (e.g., 'α', 'β-', 'β+', 'EC').
                   If None, considers all decay types (default).
        verbose: Whether to print detailed results.
        measured_activity_uncertainty: Optional uncertainty (1-sigma) for measured activity (Bq).
        include_paths: If True, include path-level details for each parent result.

    Returns:
        Calculation results dictionary.
    """
    calc = SecularEquilibriumCalculator(
        measured_nuclide,
        measured_activity,
        parent_nuclides,
        decay_type,
        measured_activity_uncertainty,
        include_paths,
    )
    results = calc.calculate()

    if verbose:
        calc.print_results(results)

    return results


if __name__ == '__main__':
    print("Running example calculations...\n")

    print("\nExample 1: Calculate U-238 series nuclides from Pb-214 activity")
    calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=100.0,
        parent_nuclides=['U-238', 'U-234', 'Ra-226', 'Rn-222'],
        verbose=True,
    )

    print("\n" + "=" * 80 + "\n")
    print("Example 2: Calculate Th-232 series nuclides from Bi-212 activity")
    calculate_secular_equilibrium(
        measured_nuclide='Bi-212',
        measured_activity=50.0,
        parent_nuclides=['Th-232', 'Ra-228', 'Th-228'],
        verbose=True,
    )
