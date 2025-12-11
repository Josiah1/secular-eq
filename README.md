# Secular Equilibrium Calculator

Radioactive Decay Chain Secular Equilibrium Calculation Tool

## 📦 Features

- Calculate parent nuclide activity and mass based on measured daughter nuclide activity
- Supports any radioactive decay chain, including natural series (U-238, Th-232, U-235) and artificial chains
- Automatic cumulative branching ratio calculation across decay chains
- Supports all decay types (α, β-, β+, EC, SF, IT, p, n, etc.)
- Decay type specification with shorthand support (a for α, b for β-, e for EC)
- Provide command-line interface (CLI) and Python API
- Detailed error handling and input validation
- Flexible output modes including quiet and mass-only outputs

## 🔧 Installation

### Install via pip (recommended)

```bash
pip install secular-equilibrium
```

### Install from source

```bash
# Clone repository
git clone https://github.com/Josiah1/secular-eq.git
cd secular-eq

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## 🚀 Quick Start

### Method 1: Python library usage

```python
from secular_equilibrium import calculate_secular_equilibrium

# Calculate U-238 content from Pb-214 activity
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=100.0,  # Bq
    parent_nuclides=['U-238', 'Ra-226'],
    verbose=True
)

print(f"U-238 activity: {results['U-238']['activity_Bq']:.4e} Bq")
print(f"U-238 mass: {results['U-238']['mass_g']:.4e} g")
```

### Method 2: Command-line usage

```bash
# Basic usage
secular-eq --measured Pb-214 --activity 100 --parents U-238 Ra-226

# Short form
secular-eq -m Pb-214 -a 100 -p U-238

# Multiple parent nuclides
secular-eq -m Bi-214 -a 50 -p U-238 U-234 Ra-226 Rn-222

# Quiet mode (only output key results)
secular-eq -m Pb-214 -a 100 -p U-238 -q

# Specify decay type (e.g., alpha decay)
secular-eq -m Pb-214 -a 100 -p U-238 -d α

# Using shorthand for decay type (a for alpha, b for beta, e for EC)
secular-eq -m Pb-214 -a 100 -p U-238 -d a

# Mass-only output (only masses in grams, one per line)
secular-eq -m Pb-214 -a 100 -p U-238 Ra-226 --mass-only
```

## 📊 Practical Application Examples

### Example 1: U-238 content determination in environmental samples

```python
from secular_equilibrium import calculate_secular_equilibrium

# Measured Pb-214 activity in soil sample is 85 Bq/kg
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=85.0,  # Bq/kg
    parent_nuclides=['U-238'],
    verbose=True
)

# Get U-238 content
u238_mass_per_kg = results['U-238']['mass_g']
u238_ppm = u238_mass_per_kg * 1e6  # Convert to ppm
print(f"\nU-238 concentration in soil: {u238_ppm:.2f} ppm")
```

### Example 2: Th-232 series analysis

```python
# Measured Bi-212 activity
results = calculate_secular_equilibrium(
    measured_nuclide='Bi-212',
    measured_activity=120.0,
    parent_nuclides=['Th-232', 'Ra-228', 'Th-228'],
    verbose=False  # Don't print detailed information
)

# Extract key information
for parent, data in results.items():
    print(f"{parent}:")
    print(f"  Activity: {data['activity_Bq']:.2e} Bq")
    print(f"  Mass: {data['mass_g']:.2e} g")
    print(f"  Branching ratio: {data['branching_ratio']:.4f}")
```

## 📚 API Documentation

### `SecularEquilibriumCalculator` class

#### Initialization parameters
- `measured_nuclide` (str): Measured nuclide name (e.g., 'Pb-214', 'Bi-214')
- `measured_activity` (float): Measured activity (Bq)
- `parent_nuclides` (List[str]): List of parent nuclides (e.g., ['U-238', 'Ra-226'])
- `decay_type` (str, optional): Decay type to consider (e.g., 'α', 'β-', 'β+', 'EC'). If None, considers all decay types (default).

#### Methods
- `calculate()`: Perform calculation, return result dictionary
- `print_results(results)`: Print formatted results

### `calculate_secular_equilibrium()` function

Convenience function that automatically creates calculator and returns results.

```python
def calculate_secular_equilibrium(
    measured_nuclide: str,
    measured_activity: float,
    parent_nuclides: List[str],
    decay_type: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Dict[str, float]]
```

#### Example with decay type specification

```python
# Calculate U-238 activity from measured Pb-214 alpha decay activity
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=50.0,  # Alpha decay activity (Bq)
    parent_nuclides=['U-238'],
    decay_type='α',  # or use shorthand 'a'
    verbose=True
)

# Using shorthand for decay type
results = calculate_secular_equilibrium(
    measured_nuclide='Pb-214',
    measured_activity=50.0,
    parent_nuclides=['U-238'],
    decay_type='a',  # shorthand for alpha
    verbose=True
)
```

#### Return value format

```python
{
    'U-238': {
        'activity_Bq': 100.0,           # Activity (Bq)
        'mass_g': 8.04e-6,              # Mass (g)
        'branching_ratio': 1.0,         # Branching ratio
        'halflife_yr': 4.468e9,         # Half-life (years)
        'atomic_mass': 238.05078826     # Atomic mass (u)
    }
}
```

## 🔬 Supported Decay Chains

The calculator supports **any radioactive decay chain** based on the nuclear decay database. While commonly used for natural radioactive series, it works equally well for artificial decay chains and custom nuclide combinations.

### Major natural radioactive series (common examples)

1. **U-238 series** (Uranium series)
   - U-238 → Th-234 → Pa-234m → U-234 → Th-230 → Ra-226 → Rn-222 → Po-218 → Pb-214 → Bi-214 → Po-214 → Pb-210

2. **Th-232 series** (Thorium series)
   - Th-232 → Ra-228 → Ac-228 → Th-228 → Ra-224 → Rn-220 → Po-216 → Pb-212 → Bi-212 → Po-212/Tl-208

3. **U-235 series** (Actinium series)
   - U-235 → Th-231 → Pa-231 → Ac-227 → Th-227 → Ra-223 → Rn-219 → Po-215 → Pb-211 → Bi-211

## ⚠️ Important Notes

1. **Closed system**: Assumes closed system with no external nuclide addition or loss
2. **Equilibrium time**: Requires waiting about 7-10 daughter half-lives to reach equilibrium
3. **Branching decay**: Automatically considers branching ratios, but ensure correct decay chain
4. **Measurement uncertainty**: Result accuracy depends on input activity measurement precision

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_calculator.py::TestSecularEquilibrium::test_u238_chain

# Use unittest
python -m unittest tests/test_calculator.py
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Contact

For questions, please submit an Issue on GitHub.
