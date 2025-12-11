"""
Secular Equilibrium Calculator for Radioactive Decay Chains

This package calculates parent nuclide activities and masses from measured
progeny activities, assuming secular equilibrium conditions.
"""

import radioactivedecay as rd
from typing import List, Dict, Tuple, Optional
import warnings


class SecularEquilibriumCalculator:
    """
    Secular equilibrium calculator for radioactive decay chains

    Attributes:
        measured_nuclide: Measured nuclide name (e.g., 'Pb-214')
        measured_activity: Measured activity (Bq)
        parent_nuclides: List of parent nuclides to consider (e.g., ['U-238', 'Ra-226'])
    """
    
    @staticmethod
    def _normalize_decay_type(decay_type: Optional[str]) -> Optional[str]:
        """
        Normalize decay type shorthand to standard notation

        Supported shorthands:
        - 'a', 'alpha' → 'α'
        - 'b', 'b-', 'beta', 'beta-' → 'β-'
        - 'b+', 'beta+' → 'β+'
        - 'e', 'ec' → 'EC'

        Also preserves original Greek letter inputs.

        Args:
            decay_type: Input decay type string or shorthand

        Returns:
            Normalized decay type string or None
        """
        if decay_type is None:
            return None

        decay_type = decay_type.strip()

        # Standard decay types (case-sensitive)
        standard_types = ['α', 'β-', 'β+', 'EC', 'SF', 'IT', 'p', 'n', 'd', 't']

        # If already in standard form, return as is
        if decay_type in standard_types:
            return decay_type

        decay_type_lower = decay_type.lower()

        # Mapping of shorthands to standard notation
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

        # Return normalized form or original if not in map
        return decay_type_map.get(decay_type_lower, decay_type)

    def __init__(self, measured_nuclide: str, measured_activity: float,
                 parent_nuclides: List[str], decay_type: Optional[str] = None):
        """
        Initialize the calculator

        Args:
            measured_nuclide: Measured nuclide name (e.g., 'Pb-214', 'Bi-214')
            measured_activity: Measured activity (Bq)
            parent_nuclides: List of parent nuclides (e.g., ['U-238', 'Th-232'])
            decay_type: Optional decay type to consider (e.g., 'α', 'β-', 'β+', 'EC').
                       If None, considers all decay types (default).
        """
        self.measured_nuclide = measured_nuclide
        self.measured_activity = measured_activity
        self.parent_nuclides = parent_nuclides
        self.decay_type = self._normalize_decay_type(decay_type)

        # Validate nuclide names and decay type
        self._validate_nuclides()

    def _validate_nuclides(self):
        """Validate that nuclide names and decay type are valid"""
        try:
            rd.Nuclide(self.measured_nuclide)
        except:
            raise ValueError(f"Invalid measured nuclide name: {self.measured_nuclide}")

        for parent in self.parent_nuclides:
            try:
                rd.Nuclide(parent)
            except:
                raise ValueError(f"Invalid parent nuclide name: {parent}")

        # Validate decay type if provided
        if self.decay_type is not None:
            if not isinstance(self.decay_type, str) or self.decay_type.strip() == '':
                raise ValueError(f"Invalid decay type: {self.decay_type}. Must be a non-empty string.")

            # Check if decay type is valid
            valid_decay_types = ['α', 'β-', 'β+', 'EC', 'SF', 'IT', 'p', 'n', 'd', 't']
            if self.decay_type not in valid_decay_types:
                raise ValueError(f"Invalid decay type: {self.decay_type}. Valid types: {', '.join(valid_decay_types)}")
    
    def _get_branching_ratio(self, parent: str, progeny: str) -> float:
        """
        Calculate cumulative branching ratio from parent to progeny

        Directly obtains decay data from radioactivedecay and recursively calculates
        the sum of branching ratio products across all possible decay paths.

        Args:
            parent: Parent nuclide
            progeny: Progeny nuclide

        Returns:
            Cumulative branching ratio (between 0 and 1)
        """
        # If it's the same nuclide
        if parent == progeny:
            return 1.0

        # Cache results to avoid repeated calculations
        if not hasattr(self, '_branching_cache'):
            self._branching_cache = {}

        cache_key = (parent, progeny, self.decay_type)
        if cache_key in self._branching_cache:
            return self._branching_cache[cache_key]

        # Get progeny nuclide info, check if it's stable
        try:
            progeny_nuclide = rd.Nuclide(progeny)
            progeny_halflife = progeny_nuclide.half_life('s')
            if progeny_halflife == float('inf'):
                raise ValueError(f"{progeny} is a stable nuclide and cannot establish secular equilibrium")
        except ValueError as e:
            # Re-raise stable nuclide errors
            raise
        except:
            raise ValueError(f"Invalid progeny nuclide name: {progeny}")

        # Recursively calculate cumulative branching ratio
        def calculate_ratio(current: str, target: str, visited: set, depth: int) -> float:
            """Recursive helper function"""
            if depth > 30:  # Limit recursion depth to avoid infinite loops
                return 0.0

            if current in visited:
                return 0.0  # Avoid cycles

            visited.add(current)

            # If we've reached the target
            if current == target:
                visited.remove(current)
                # If decay type is specified, return the branching fraction for that decay type
                if self.decay_type is not None:
                    try:
                        target_nuclide = rd.Nuclide(target)
                        modes = target_nuclide.decay_modes()
                        fractions = target_nuclide.branching_fractions()

                        matching_fraction = 0.0
                        for mode, fraction in zip(modes, fractions):
                            if self.decay_type in mode:
                                matching_fraction += fraction

                        return matching_fraction
                    except:
                        return 0.0
                else:
                    return 1.0

            try:
                nuclide = rd.Nuclide(current)
            except:
                visited.remove(current)
                return 0.0

            # Get decay modes, branching fractions, and progeny
            modes = nuclide.decay_modes()
            fractions = nuclide.branching_fractions()
            progeny_list = nuclide.progeny()

            total_ratio = 0.0

            for mode, fraction, child in zip(modes, fractions, progeny_list):
                # Skip non-nuclide decay products (e.g., SF, EC, etc.)
                if child in ['SF', 'EC', 'β+', 'β-', 'α', 'IT', 'p', 'n', 'd', 't']:
                    continue

                # Recursively calculate child to target ratio
                child_ratio = calculate_ratio(child, target, visited.copy(), depth + 1)
                total_ratio += fraction * child_ratio

            visited.remove(current)
            return total_ratio

        # Start calculation
        branching_ratio = calculate_ratio(parent, progeny, set(), 0)

        # If branching ratio is 0 or very small (< 1e-15), progeny is not in decay chain
        if branching_ratio < 1e-15:
            raise ValueError(f"{progeny} is not in {parent}'s decay chain")

        # Cache valid result
        self._branching_cache[cache_key] = branching_ratio

        return branching_ratio
    
    
    def calculate(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate activities and masses for parent nuclides

        Returns:
            Dictionary with format:
            {
                'parent_name': {
                    'activity_Bq': float,
                    'mass_g': float,
                    'branching_ratio': float,
                    'halflife_yr': float
                }
            }
        """
        results = {}

        for parent in self.parent_nuclides:

            # Get branching ratio
            try:
                branching_ratio = self._get_branching_ratio(parent, self.measured_nuclide)
            except ValueError as e:
                # Catch branching ratio calculation errors (stable nuclide, invalid nuclide, not in decay chain, etc.)
                results[parent] = {
                    'activity_Bq': 0.0,
                    'mass_g': 0.0,
                    'branching_ratio': 0.0,
                    'halflife_yr': 0.0,
                    'error': str(e)  # Use specific error message
                }
                continue

            # Under secular equilibrium: A_parent * BR = A_measured
            parent_activity = self.measured_activity / branching_ratio
            
            # Get parent nuclide information
            parent_nuclide = rd.Nuclide(parent)
            parent_halflife_s = parent_nuclide.half_life('s')
            parent_halflife_yr = parent_halflife_s / (365.25 * 24 * 3600)
            parent_mass_amu = parent_nuclide.atomic_mass
            
            # Calculate mass
            # N = A / λ, λ = ln(2) / t_half
            # mass = N * (atomic_mass / N_A)
            import math
            N_A = 6.02214076e23  # Avogadro's number
            
            if parent_halflife_s == float('inf'):
                # Stable nuclide, cannot calculate mass from activity
                parent_mass = float('inf')
            else:
                lambda_parent = math.log(2) / parent_halflife_s
                N_atoms = parent_activity / lambda_parent
                parent_mass = N_atoms * parent_mass_amu / N_A
            
            results[parent] = {
                'activity_Bq': parent_activity,
                'mass_g': parent_mass,
                'branching_ratio': branching_ratio,
                'halflife_yr': parent_halflife_yr,
                'atomic_mass': parent_mass_amu
            }
        
        return results
    
    def print_results(self, results: Optional[Dict] = None):
        """
        Print calculation results

        Args:
            results: Calculation results dictionary (if None, recalculate)
        """
        if results is None:
            results = self.calculate()
        
        print("=" * 80)
        print("Secular Equilibrium Calculation Results")
        print("=" * 80)
        print(f"\nMeasured nuclide: {self.measured_nuclide}")
        print(f"Measured activity: {self.measured_activity:.4e} Bq")
        print("\n" + "-" * 80)
        
        for parent, data in results.items():
            print(f"\nParent nuclide: {parent}")

            if 'error' in data:
                print(f"  Error: {data['error']}")
                print(f"  Branching ratio ({parent} → {self.measured_nuclide}): {data['branching_ratio']:.6f}")
            else:
                print(f"  Half-life: {data['halflife_yr']:.4e} years")
                print(f"  Atomic mass: {data['atomic_mass']:.4f} u")
                print(f"  Branching ratio ({parent} → {self.measured_nuclide}): {data['branching_ratio']:.6f}")

                print(f"  Calculated activity: {data['activity_Bq']:.4e} Bq")
                if data['mass_g'] == float('inf'):
                    print(f"  Mass: Cannot calculate (stable nuclide)")
                else:
                    print(f"  Mass: {data['mass_g']:.4e} g")
                    if data['mass_g'] < 1e-6:
                        print(f"       {data['mass_g']*1e9:.4e} ng")
                    elif data['mass_g'] < 1e-3:
                        print(f"       {data['mass_g']*1e6:.4e} µg")
                    elif data['mass_g'] < 1:
                        print(f"       {data['mass_g']*1e3:.4e} mg")
        
        print("\n" + "=" * 80)


def calculate_secular_equilibrium(measured_nuclide: str,
                                  measured_activity: float,
                                  parent_nuclides: List[str],
                                  decay_type: Optional[str] = None,
                                  verbose: bool = True) -> Dict[str, Dict[str, float]]:
    """
    Convenience function: Calculate secular equilibrium for radioactive decay chains

    Args:
        measured_nuclide: Measured nuclide name (e.g., 'Pb-214')
        measured_activity: Measured activity (Bq)
        parent_nuclides: Parent nuclides list (e.g., ['U-238', 'Ra-226'])
        decay_type: Optional decay type to consider (e.g., 'α', 'β-', 'β+', 'EC').
                   If None, considers all decay types (default).
        verbose: Whether to print detailed results

    Returns:
        Calculation results dictionary
    """
    calc = SecularEquilibriumCalculator(measured_nuclide, measured_activity, parent_nuclides, decay_type)
    results = calc.calculate()

    if verbose:
        calc.print_results(results)

    return results


if __name__ == '__main__':
    # If run as a script directly, run examples
    print("Running example calculations...\n")
    
    # Example 1: U-238 decay chain
    print("\nExample 1: Calculate U-238 series nuclides from Pb-214 activity")
    calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=100.0,  # Bq
        parent_nuclides=['U-238', 'U-234', 'Ra-226', 'Rn-222'],
        verbose=True
    )
    
    # Example 2: Th-232 decay chain
    print("\n" + "="*80 + "\n")
    print("Example 2: Calculate Th-232 series nuclides from Bi-212 activity")
    calculate_secular_equilibrium(
        measured_nuclide='Bi-212',
        measured_activity=50.0,  # Bq
        parent_nuclides=['Th-232', 'Ra-228', 'Th-228'],
        verbose=True
    )