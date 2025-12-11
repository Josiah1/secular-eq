"""
Command Line Interface for Secular Equilibrium Calculator
Command line interface for secular equilibrium calculator
"""

import argparse
import sys
from .calculator import calculate_secular_equilibrium


def main():
    """Command line main function"""
    parser = argparse.ArgumentParser(
        description='Secular Equilibrium Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate U-238 content from Pb-214 activity
  secular-eq --measured Pb-214 --activity 100 --parents U-238 Ra-226

  # Using shorthand arguments
  secular-eq -m Pb-214 -a 100 -p U-238

  # Calculate Th-232 content from Bi-214 activity
  secular-eq -m Bi-214 -a 50 -p Th-232 Ra-228

  # Analyze multiple parent nuclides
  secular-eq -m Pb-214 -a 120 -p U-238 U-234 Ra-226 Rn-222
        """
    )
    
    parser.add_argument(
        '-m', '--measured',
        required=True,
        help='Measured nuclide name (e.g., Pb-214, Bi-214, Tl-208)'
    )
    
    parser.add_argument(
        '-a', '--activity',
        type=float,
        required=True,
        help='Measured activity in Bq'
    )
    
    parser.add_argument(
        '-p', '--parents',
        nargs='+',
        required=True,
        help='Parent nuclides list (e.g., U-238 Ra-226)'
    )

    parser.add_argument(
        '-d', '--decay-type',
        help='Decay type to consider. Native types: α, β-, β+, EC, SF, IT, p, n, d, t. '
             'Shorthand support: a/alpha for α, b/beta for β-, b+/beta+ for β+, e/ec for EC. '
             'If not specified, considers all decay types.'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode, output key results only'
    )

    parser.add_argument(
        '--mass-only',
        action='store_true',
        help='Output only masses (in grams) in the order of input parent nuclides'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.1'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Determine verbose mode
        if args.mass_only:
            verbose = False
        else:
            verbose = not args.quiet

        # Perform calculation
        results = calculate_secular_equilibrium(
            measured_nuclide=args.measured,
            measured_activity=args.activity,
            parent_nuclides=args.parents,
            decay_type=args.decay_type,
            verbose=verbose
        )

        # If mass-only mode, output only masses in order of input parent nuclides
        if args.mass_only:
            output_parts = []
            for parent in args.parents:
                data = results.get(parent)
                if data and 'error' not in data:
                    mass = data['mass_g']
                    if mass == float('inf'):
                        output_parts.append('inf')
                    else:
                        output_parts.append(f"{mass:.4e}")
                else:
                    output_parts.append('NaN')
            print(" ".join(output_parts))
            return 0

        # If quiet mode, output only numbers in one line
        if args.quiet:
            output_parts = []
            for parent in args.parents:
                data = results.get(parent)
                if data and 'error' not in data:
                    activity = data['activity_Bq']
                    mass = data['mass_g']
                    if mass == float('inf'):
                        output_parts.append(f"{activity:.4e} inf")
                    else:
                        output_parts.append(f"{activity:.4e} {mass:.4e}")
                else:
                    output_parts.append("NaN NaN")
            print(" ".join(output_parts))

        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
