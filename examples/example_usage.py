"""
Secular Equilibrium Calculator - Detailed usage examples
Demonstrates various application scenarios
"""

from secular_equilibrium import calculate_secular_equilibrium, SecularEquilibriumCalculator


def example1_basic_usage():
    """Example 1: Basic usage - Calculate U-238 content from Pb-214 activity"""
    print("\n" + "="*80)
    print("Example 1: Basic usage - U-238 determination in environmental samples")
    print("="*80)
    
    # Scenario: Measured Pb-214 gamma rays in soil sample, obtained activity of 100 Bq/kg
    results = calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=100.0,  # Bq/kg
        parent_nuclides=['U-238'],
        verbose=True
    )
    
    # Extract key information
    u238_mass = results['U-238']['mass_g']
    u238_ppm = u238_mass * 1e6  # Convert to ppm (µg/g)
    
    print(f"\nConclusion: U-238 concentration in this soil sample is approximately {u238_ppm:.2f} ppm")


def example2_full_decay_chain():
    """Example 2: Full decay chain analysis - Analyze multiple nuclides in U-238 decay chain"""
    print("\n" + "="*80)
    print("Example 2: Full decay chain analysis")
    print("="*80)
    
    # Measure Pb-214 activity, calculate content of multiple nuclides in decay chain
    calc = SecularEquilibriumCalculator(
        measured_nuclide='Pb-214',
        measured_activity=150.0,  # Bq
        parent_nuclides=['U-238', 'U-234', 'Th-230', 'Ra-226', 'Rn-222', 'Po-218']
    )
    
    results = calc.calculate()
    calc.print_results(results)
    
    # Analyze results
    print("\nDetailed analysis:")
    print(f"From measured Pb-214 activity ({calc.measured_activity} Bq) can deduce:")
    for parent in ['U-238', 'Ra-226', 'Rn-222']:
        if parent in results:
            data = results[parent]
            print(f"\n{parent}:")
            print(f"  Activity: {data['activity_Bq']:.4e} Bq")
            print(f"  Mass: {data['mass_g']:.4e} g")
            print(f"  Half-life: {data['halflife_yr']:.4e} years")


def example3_thorium_series():
    """Example 3: Th-232 series analysis"""
    print("\n" + "="*80)
    print("Example 3: Th-232 series analysis")
    print("="*80)
    
    # Measure Bi-212 activity
    results = calculate_secular_equilibrium(
        measured_nuclide='Bi-212',
        measured_activity=75.0,  # Bq
        parent_nuclides=['Th-232', 'Ra-228', 'Th-228', 'Ra-224'],
        verbose=True
    )
    
    # Compare content of different nuclides
    print("\nNuclide content comparison:")
    masses = {k: v['mass_g'] for k, v in results.items() if 'mass_g' in v}
    for nuclide, mass in sorted(masses.items(), key=lambda x: x[1], reverse=True):
        print(f"{nuclide:10s}: {mass:.4e} g")


def example4_batch_processing():
    """Example 4: Batch processing of multiple samples"""
    print("\n" + "="*80)
    print("Example 4: Batch processing of multiple samples")
    print("="*80)

    # Assume measurement data for multiple samples
    samples_data = {
        'Sample_A': {'nuclide': 'Pb-214', 'activity': 100.0},
        'Sample_B': {'nuclide': 'Pb-214', 'activity': 85.3},
        'Sample_C': {'nuclide': 'Bi-214', 'activity': 92.5},
        'Sample_D': {'nuclide': 'Pb-214', 'activity': 115.8},
    }

    # Target parent nuclides to calculate
    target_parents = ['U-238', 'Ra-226']

    # Store all results
    all_results = {}

    print("\nProcessing multiple samples...")
    for sample_id, data in samples_data.items():
        print(f"\nProcessing {sample_id}...")

        calc = SecularEquilibriumCalculator(
            measured_nuclide=data['nuclide'],
            measured_activity=data['activity'],
            parent_nuclides=target_parents
        )

        results = calc.calculate()
        all_results[sample_id] = results

        # Extract U-238 information
        u238_data = results['U-238']
        print(f"  Measured nuclide: {data['nuclide']}, Activity: {data['activity']:.2f} Bq")
        print(f"  → U-238 activity: {u238_data['activity_Bq']:.2f} Bq")
        print(f"  → U-238 mass: {u238_data['mass_g']:.4e} g ({u238_data['mass_g']*1e6:.2f} µg)")

    # Statistical analysis
    print("\n" + "-"*80)
    print("Statistical summary:")
    u238_activities = [r['U-238']['activity_Bq'] for r in all_results.values()]
    u238_masses = [r['U-238']['mass_g'] for r in all_results.values()]

    import statistics
    print(f"U-238 activity range: {min(u238_activities):.2f} - {max(u238_activities):.2f} Bq")
    print(f"U-238 activity average: {statistics.mean(u238_activities):.2f} Bq")
    print(f"U-238 mass range: {min(u238_masses):.4e} - {max(u238_masses):.4e} g")
    print(f"U-238 mass average: {statistics.mean(u238_masses):.4e} g")


def example5_comparing_measurement_methods():
    """Example 5: Comparing results from different measurement nuclides"""
    print("\n" + "="*80)
    print("Example 5: Comparing results from different measurement nuclides")
    print("="*80)

    # Assuming under secular equilibrium, activities of different daughter nuclides in the same sample are measured
    # Theoretically, they should yield the same parent nuclide content

    measured_nuclides = {
        'Pb-214': 100.0,
        'Bi-214': 100.0,
        'Po-218': 100.0,
    }

    print("\nAssuming ideal secular equilibrium, multiple daughter nuclides in the same sample are measured:")

    u238_results = {}

    for nuclide, activity in measured_nuclides.items():
        print(f"\nFrom {nuclide} measurement (activity: {activity} Bq):")

        results = calculate_secular_equilibrium(
            measured_nuclide=nuclide,
            measured_activity=activity,
            parent_nuclides=['U-238'],
            verbose=False
        )

        u238_activity = results['U-238']['activity_Bq']
        u238_mass = results['U-238']['mass_g']
        branching_ratio = results['U-238']['branching_ratio']

        print(f"  Branching ratio: {branching_ratio:.6f}")
        print(f"  Derived U-238 activity: {u238_activity:.4e} Bq")
        print(f"  Derived U-238 mass: {u238_mass:.4e} g")

        u238_results[nuclide] = u238_activity

    # Check consistency of results
    print("\n" + "-"*80)
    print("Result consistency check:")
    activities = list(u238_results.values())
    if max(activities) - min(activities) < 0.01:
        print("✓ All measurement methods yield consistent U-238 activity, validating secular equilibrium assumption")
    else:
        print("⚠ Different measurement methods show discrepancies, may not be in complete equilibrium")


def example6_concentration_calculation():
    """Example 6: Concentration unit conversion (Bq/kg ↔ g/g)"""
    print("\n" + "="*80)
    print("Example 6: Concentration unit conversion example")
    print("="*80)

    # Scenario: Measured 1kg soil sample
    sample_mass_kg = 1.0
    measured_activity_total = 120.0  # Total activity of the entire sample (Bq)

    # Convert to specific activity
    measured_activity_per_kg = measured_activity_total / sample_mass_kg  # Bq/kg

    print(f"Sample mass: {sample_mass_kg} kg")
    print(f"Measured Pb-214 total activity: {measured_activity_total} Bq")
    print(f"Pb-214 specific activity: {measured_activity_per_kg} Bq/kg")

    # Calculate U-238 content
    results = calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=measured_activity_total,
        parent_nuclides=['U-238'],
        verbose=False
    )

    u238_mass_total_g = results['U-238']['mass_g']
    u238_concentration_g_per_g = u238_mass_total_g / (sample_mass_kg * 1000)
    u238_concentration_ppm = u238_concentration_g_per_g * 1e6
    u238_concentration_ppb = u238_concentration_g_per_g * 1e9

    print(f"\nU-238 content:")
    print(f"  Total mass: {u238_mass_total_g:.4e} g")
    print(f"  Concentration (g/g): {u238_concentration_g_per_g:.4e}")
    print(f"  Concentration (ppm): {u238_concentration_ppm:.2f}")
    print(f"  Concentration (ppb): {u238_concentration_ppb:.2f}")

    # Specific activity calculation
    u238_activity_per_kg = results['U-238']['activity_Bq'] / sample_mass_kg
    print(f"\nU-238 activity:")
    print(f"  Total activity: {results['U-238']['activity_Bq']:.2f} Bq")
    print(f"  Specific activity: {u238_activity_per_kg:.2f} Bq/kg")
    print(f"  Specific activity: {u238_activity_per_kg/1000:.2f} Bq/g")


def example7_error_handling():
    """Example 7: Error handling and edge cases"""
    print("\n" + "="*80)
    print("Example 7: Error handling examples")
    print("="*80)

    # Test 1: Invalid nuclide name
    print("\nTest 1: Invalid nuclide name")
    try:
        results = calculate_secular_equilibrium(
            measured_nuclide='Invalid-999',
            measured_activity=100.0,
            parent_nuclides=['U-238'],
            verbose=False
        )
    except ValueError as e:
        print(f"✓ Correctly caught error: {e}")

    # Test 2: Nuclide not in decay chain
    print("\nTest 2: Nuclide not in decay chain")
    results = calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=100.0,
        parent_nuclides=['Th-232', 'U-238'],  # Th-232 is not in U series
        verbose=False
    )

    print("Th-232 branching ratio:", results['Th-232']['branching_ratio'])
    print("U-238 branching ratio:", results['U-238']['branching_ratio'])

    # Test 3: Secular equilibrium condition check
    print("\nTest 3: Secular equilibrium condition check (parent half-life not long enough)")
    results = calculate_secular_equilibrium(
        measured_nuclide='Pb-214',
        measured_activity=100.0,
        parent_nuclides=['Rn-222'],  # Rn-222 has short half-life
        verbose=False
    )


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("Radioactive Decay Chain Secular Equilibrium Calculator - Example Suite")
    print("Secular Equilibrium Calculator - Example Suite")
    print("="*80)

    examples = [
        ("Basic usage", example1_basic_usage),
        ("Full decay chain analysis", example2_full_decay_chain),
        ("Th-232 series", example3_thorium_series),
        ("Batch processing", example4_batch_processing),
        ("Comparing measurement methods", example5_comparing_measurement_methods),
        ("Concentration unit conversion", example6_concentration_calculation),
        ("Error handling", example7_error_handling),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "="*80)
    choice = input("\nSelect example to run (1-7, or press Enter to run all): ").strip()

    if choice == "":
        # Run all examples
        for name, func in examples:
            func()
            input("\nPress Enter to continue to next example...")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        # Run selected example
        name, func = examples[int(choice) - 1]
        func()
    else:
        print("Invalid selection")

    print("\n" + "="*80)
    print("Example demonstration completed!")
    print("="*80)


if __name__ == '__main__':
    main()
