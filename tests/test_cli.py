import csv
import io
import os
import subprocess
import sys
import tempfile
import unittest


class TestSecularEquilibriumCLI(unittest.TestCase):

    def _run_cli(self, args):
        cmd = [sys.executable, '-m', 'secular_equilibrium.cli'] + args
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_quiet_output_with_uncertainty(self):
        """Quiet mode should include uncertainty values when --activity-unc is used."""
        proc = self._run_cli([
            '-m', 'Pb-214',
            '-a', '100',
            '-p', 'U-238',
            '-q',
            '--activity-unc', '5',
        ])

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        parts = proc.stdout.strip().split()
        self.assertEqual(len(parts), 4)

    def test_explain_paths_output(self):
        """Human-readable mode should print path contribution details."""
        proc = self._run_cli([
            '-m', 'Ra-223',
            '-a', '100',
            '-p', 'Ac-227',
            '--explain-paths',
        ])

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn('Path contributions:', proc.stdout)
        self.assertIn('Ac-227 ->', proc.stdout)

    def test_batch_csv_stdout(self):
        """Batch mode should emit CSV to stdout when --output-csv is omitted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_csv = os.path.join(tmpdir, 'input.csv')
            with open(input_csv, 'w', encoding='utf-8', newline='') as fh:
                writer = csv.writer(fh)
                writer.writerow([
                    'measured_nuclide',
                    'measured_activity',
                    'parent_nuclides',
                    'decay_type',
                    'measured_activity_uncertainty',
                ])
                writer.writerow(['Pb-214', '100', 'U-238;Ra-226', '', '5'])

            proc = self._run_cli(['--input-csv', input_csv])
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)

            reader = csv.DictReader(io.StringIO(proc.stdout))
            rows = list(reader)
            self.assertEqual(len(rows), 2)

            parents = {row['parent'] for row in rows}
            self.assertEqual(parents, {'U-238', 'Ra-226'})
            for row in rows:
                self.assertEqual(row['error'], '')

    def test_batch_csv_output_file_with_row_error(self):
        """Batch mode should continue on row errors and exit with code 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_csv = os.path.join(tmpdir, 'input.csv')
            output_csv = os.path.join(tmpdir, 'output.csv')

            with open(input_csv, 'w', encoding='utf-8', newline='') as fh:
                writer = csv.writer(fh)
                writer.writerow([
                    'measured_nuclide',
                    'measured_activity',
                    'parent_nuclides',
                    'decay_type',
                    'measured_activity_uncertainty',
                ])
                writer.writerow(['Pb-214', '100', 'U-238', '', ''])
                writer.writerow(['Invalid-999', '100', 'U-238', '', ''])

            proc = self._run_cli(['--input-csv', input_csv, '--output-csv', output_csv])
            self.assertEqual(proc.returncode, 1)
            self.assertTrue(os.path.exists(output_csv))

            with open(output_csv, 'r', encoding='utf-8', newline='') as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)

            self.assertTrue(any(row['parent'] == 'U-238' and row['error'] == '' for row in rows))
            self.assertTrue(any('Invalid measured nuclide name' in row['error'] for row in rows))


if __name__ == '__main__':
    unittest.main()
