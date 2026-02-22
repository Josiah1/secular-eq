"""
Command-line interface for secular equilibrium calculator.
"""

import argparse
import csv
import json
import sys
from typing import Dict, List, Optional, Tuple

from . import __version__
from .calculator import calculate_secular_equilibrium


def _parse_parent_nuclides(raw_value: str) -> List[str]:
    """Parse parent nuclide list from semicolon/comma/space-separated text."""
    text = (raw_value or '').strip()
    if not text:
        return []

    if ';' in text:
        parts = text.split(';')
    elif ',' in text:
        parts = text.split(',')
    else:
        parts = text.split()

    return [item.strip() for item in parts if item.strip()]


def _parse_optional_float(raw_value: Optional[str]) -> Optional[float]:
    """Parse optional float, returning None for blank input."""
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    if text == '':
        return None
    return float(text)


def _format_mass(value: float) -> str:
    if value == float('inf'):
        return 'inf'
    return '{0:.4e}'.format(value)


def _format_activity(value: float) -> str:
    if value == float('inf'):
        return 'inf'
    return '{0:.4e}'.format(value)


def _csv_value(value):
    """Serialize output value for CSV."""
    if value is None:
        return ''
    if isinstance(value, float):
        if value == float('inf'):
            return 'inf'
        if value == float('-inf'):
            return '-inf'
        return '{0:.12e}'.format(value)
    return value


def _build_batch_output_rows(args) -> Tuple[List[Dict[str, str]], bool]:
    """Process input CSV and return output rows plus error status."""
    required_columns = ['measured_nuclide', 'measured_activity', 'parent_nuclides']
    rows = []
    had_errors = False

    with open(args.input_csv, 'r', encoding='utf-8', newline='') as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError('Input CSV is missing header row')

        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            raise ValueError('Missing required CSV columns: {0}'.format(', '.join(missing)))

        for index, input_row in enumerate(reader, start=2):
            measured_nuclide = (input_row.get('measured_nuclide') or '').strip()
            measured_activity_text = (input_row.get('measured_activity') or '').strip()
            parent_nuclides_text = (input_row.get('parent_nuclides') or '').strip()
            decay_type_text = (input_row.get('decay_type') or '').strip() or None
            unc_text = (input_row.get('measured_activity_uncertainty') or '').strip()

            row_base = {
                'input_row': index,
                'measured_nuclide': measured_nuclide,
                'measured_activity': measured_activity_text,
                'parent_nuclides': parent_nuclides_text,
                'decay_type': decay_type_text or '',
                'measured_activity_uncertainty': unc_text,
            }

            try:
                measured_activity = float(measured_activity_text)
                parent_nuclides = _parse_parent_nuclides(parent_nuclides_text)
                measured_activity_uncertainty = _parse_optional_float(unc_text)

                if not measured_nuclide:
                    raise ValueError('row {0}: measured_nuclide is empty'.format(index))
                if not parent_nuclides:
                    raise ValueError('row {0}: parent_nuclides is empty'.format(index))

                results = calculate_secular_equilibrium(
                    measured_nuclide=measured_nuclide,
                    measured_activity=measured_activity,
                    parent_nuclides=parent_nuclides,
                    decay_type=decay_type_text,
                    measured_activity_uncertainty=measured_activity_uncertainty,
                    include_paths=args.explain_paths,
                    verbose=False,
                )

                for parent in parent_nuclides:
                    data = results.get(parent, {})
                    error = data.get('error', '')
                    if error:
                        had_errors = True

                    paths_json = ''
                    if args.explain_paths and 'paths' in data:
                        paths_json = json.dumps(data['paths'], ensure_ascii=False)

                    rows.append({
                        **row_base,
                        'parent': parent,
                        'activity_Bq': _csv_value(data.get('activity_Bq')),
                        'mass_g': _csv_value(data.get('mass_g')),
                        'branching_ratio': _csv_value(data.get('branching_ratio')),
                        'halflife_yr': _csv_value(data.get('halflife_yr')),
                        'atomic_mass': _csv_value(data.get('atomic_mass')),
                        'activity_uncertainty_Bq': _csv_value(data.get('activity_uncertainty_Bq')),
                        'mass_uncertainty_g': _csv_value(data.get('mass_uncertainty_g')),
                        'relative_uncertainty': _csv_value(data.get('relative_uncertainty')),
                        'paths_json': paths_json,
                        'error': error,
                    })

            except Exception as exc:
                had_errors = True
                rows.append({
                    **row_base,
                    'parent': '',
                    'activity_Bq': '',
                    'mass_g': '',
                    'branching_ratio': '',
                    'halflife_yr': '',
                    'atomic_mass': '',
                    'activity_uncertainty_Bq': '',
                    'mass_uncertainty_g': '',
                    'relative_uncertainty': '',
                    'paths_json': '',
                    'error': str(exc),
                })

    return rows, had_errors


def _write_batch_output(rows: List[Dict[str, str]], output_csv: Optional[str]):
    """Write batch rows to stdout or output file."""
    fieldnames = [
        'input_row',
        'measured_nuclide',
        'measured_activity',
        'parent_nuclides',
        'decay_type',
        'measured_activity_uncertainty',
        'parent',
        'activity_Bq',
        'mass_g',
        'branching_ratio',
        'halflife_yr',
        'atomic_mass',
        'activity_uncertainty_Bq',
        'mass_uncertainty_g',
        'relative_uncertainty',
        'paths_json',
        'error',
    ]

    if output_csv:
        with open(output_csv, 'w', encoding='utf-8', newline='') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _run_single_mode(args) -> int:
    """Run single-case CLI mode."""
    verbose = not args.quiet and not args.mass_only

    results = calculate_secular_equilibrium(
        measured_nuclide=args.measured,
        measured_activity=args.activity,
        parent_nuclides=args.parents,
        decay_type=args.decay_type,
        measured_activity_uncertainty=args.activity_unc,
        include_paths=args.explain_paths,
        verbose=verbose,
    )

    if args.mass_only:
        output_parts = []
        for parent in args.parents:
            data = results.get(parent)
            if data and 'error' not in data:
                output_parts.append(_format_mass(data['mass_g']))
            else:
                output_parts.append('NaN')
        print(' '.join(output_parts))
        return 0

    if args.quiet:
        output_parts = []
        for parent in args.parents:
            data = results.get(parent)
            if data and 'error' not in data:
                activity = _format_activity(data['activity_Bq'])
                mass = _format_mass(data['mass_g'])
                if args.activity_unc is not None and 'activity_uncertainty_Bq' in data:
                    a_unc = _format_activity(data['activity_uncertainty_Bq'])
                    m_unc = _format_mass(data['mass_uncertainty_g'])
                    output_parts.append('{0} {1} {2} {3}'.format(activity, mass, a_unc, m_unc))
                else:
                    output_parts.append('{0} {1}'.format(activity, mass))
            else:
                if args.activity_unc is not None:
                    output_parts.append('NaN NaN NaN NaN')
                else:
                    output_parts.append('NaN NaN')
        print(' '.join(output_parts))

    return 0


def _run_batch_mode(args) -> int:
    """Run CSV batch mode."""
    if args.mass_only:
        raise ValueError('--mass-only is not supported in batch mode')

    if args.measured or args.activity is not None or args.parents:
        raise ValueError('--input-csv cannot be combined with --measured/--activity/--parents')

    rows, had_errors = _build_batch_output_rows(args)
    _write_batch_output(rows, args.output_csv)
    return 1 if had_errors else 0


def main():
    """Command line main function."""
    parser = argparse.ArgumentParser(
        description='Secular Equilibrium Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single-case calculation
  secular-eq --measured Pb-214 --activity 100 --parents U-238 Ra-226

  # Include measurement uncertainty
  secular-eq -m Pb-214 -a 100 -p U-238 --activity-unc 5

  # Explain all decay paths and path contributions
  secular-eq -m Ra-223 -a 100 -p Ac-227 --explain-paths

  # Batch mode from CSV
  secular-eq --input-csv batch_inputs.csv

  # Batch mode to output file
  secular-eq --input-csv batch_inputs.csv --output-csv batch_outputs.csv
        """,
    )

    parser.add_argument(
        '-m', '--measured',
        help='Measured nuclide name (e.g., Pb-214, Bi-214, Tl-208)'
    )

    parser.add_argument(
        '-a', '--activity',
        type=float,
        help='Measured activity in Bq'
    )

    parser.add_argument(
        '-p', '--parents',
        nargs='+',
        help='Parent nuclides list (e.g., U-238 Ra-226)'
    )

    parser.add_argument(
        '-d', '--decay-type',
        help='Decay type to consider. Native types: α, β-, β+, EC, SF, IT, p, n, d, t. '
             'Shorthand support: a/alpha for α, b/beta for β-, b+/beta+ for β+, e/ec for EC. '
             'If not specified, considers all decay types.'
    )

    parser.add_argument(
        '--activity-unc',
        type=float,
        help='Measured activity uncertainty (1-sigma, Bq)'
    )

    parser.add_argument(
        '--explain-paths',
        action='store_true',
        help='Include detailed parent->measured decay path contributions'
    )

    parser.add_argument(
        '--input-csv',
        help='Batch mode input CSV path. Required columns: measured_nuclide, measured_activity, parent_nuclides. '
             'Optional columns: decay_type, measured_activity_uncertainty. '
             'Use semicolon-separated parent_nuclides (e.g., U-238;Ra-226).'
    )

    parser.add_argument(
        '--output-csv',
        help='Batch mode output CSV path. Defaults to stdout when omitted.'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode, output key numeric results only'
    )

    parser.add_argument(
        '--mass-only',
        action='store_true',
        help='Output only masses (in grams) in the order of input parent nuclides'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s {0}'.format(__version__)
    )

    args = parser.parse_args()

    try:
        if args.input_csv:
            return _run_batch_mode(args)

        if args.output_csv:
            raise ValueError('--output-csv requires --input-csv')

        missing = []
        if not args.measured:
            missing.append('--measured')
        if args.activity is None:
            missing.append('--activity')
        if not args.parents:
            missing.append('--parents')
        if missing:
            raise ValueError('Single-case mode requires: {0}'.format(', '.join(missing)))

        return _run_single_mode(args)

    except Exception as exc:
        print('Error: {0}'.format(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
