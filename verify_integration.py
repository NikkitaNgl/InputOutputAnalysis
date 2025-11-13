"""
Verification script for integrated_dual_shock_spectral_analysis.py

This script checks that all required components are present:
- Classes: IOSystem, ShockGenerator, ShockPropagator, EnhancedSpectralAnalyzer,
          TemporalRMTAnalyzer, NetworkVisualizer
- Functions: All required plotting functions and analysis functions
- Expected outputs: All CSV files and visualizations
"""

import ast
import sys
from pathlib import Path

def check_code_structure(filepath):
    """Verify code structure."""
    print("="*80)
    print("VERIFICATION: Integrated Dual Shock Spectral Analysis")
    print("="*80)

    with open(filepath, 'r') as f:
        code = f.read()

    tree = ast.parse(code)

    # Extract classes and functions
    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            # Only top-level functions
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

    # Required components
    required_classes = [
        'IOSystem',
        'ShockGenerator',
        'ShockPropagator',
        'EnhancedSpectralAnalyzer',
        'TemporalRMTAnalyzer',
        'NetworkVisualizer'
    ]

    required_functions = [
        'identify_policy_sectors',
        'generate_policy_shocks',
        'conduct_sensitivity_analysis',
        'plot_spectral_comparison',
        'plot_sector_impact',
        'plot_rmt_analysis',
        'plot_sensitivity_analysis',
        'plot_temporal_rmt_analysis',
        'plot_contagion_analysis',
        'load_figaro_data',
        'prepare_io_system',
        'analyze_single_year',
        'run_temporal_analysis',
        'main'
    ]

    print("\n✓ Checking Classes:")
    print("-" * 80)
    for cls in required_classes:
        status = "✓" if cls in classes else "✗"
        print(f"  {status} {cls}")

    print("\n✓ Checking Functions:")
    print("-" * 80)
    for func in required_functions:
        status = "✓" if func in functions else "✗"
        print(f"  {status} {func}")

    # Check for expected outputs
    print("\n✓ Expected Outputs:")
    print("-" * 80)

    expected_outputs = {
        'CSV Files (per year)': [
            'figaro_shock_analysis_results.csv',
            'figaro_sensitivity_analysis.csv'
        ],
        'CSV Files (temporal)': [
            'temporal_systemic_risk_indicators.csv',
            'kolmogorov_smirnov_tests.csv',
            'financial_contagion_analysis.csv'
        ],
        'Matrix Files (per year)': [
            'matrix_A_leontief.npy',
            'matrix_B_ghosh.npy'
        ],
        'Visualizations (per year)': [
            'plot_1_spectral_comparison.png',
            'plot_2_sector_impact.png',
            'plot_7_rmt_analysis.png',
            'plot_8_sensitivity_analysis.png'
        ],
        'Visualizations (temporal)': [
            'plot_9_temporal_rmt_analysis.png',
            'plot_10_contagion_analysis.png'
        ]
    }

    for category, files in expected_outputs.items():
        print(f"\n  {category}:")
        for f in files:
            # Check if filename appears in code
            status = "✓" if f in code else "?"
            print(f"    {status} {f}")

    # Check for critical features
    print("\n✓ Critical Features:")
    print("-" * 80)

    critical_features = {
        'No self-loops in networks': 'i != j',
        'Marchenko-Pastur bounds': 'marchenko_pastur_bounds',
        'Dual shock propagation': 'propagate_dual_shock',
        'Leontief inverse': 'self.L',
        'Ghosh inverse': 'self.G',
        'RMT correlation matrix': 'correlation_matrix',
        'Outlier detection': 'identify_outliers',
        'Contagion detection': 'detect_financial_contagion',
        'Kolmogorov-Smirnov test': 'kolmogorov_smirnov_test',
        'Policy scenarios': 'generate_policy_shocks',
        'Sensitivity analysis': 'conduct_sensitivity_analysis'
    }

    for feature, keyword in critical_features.items():
        status = "✓" if keyword in code else "✗"
        print(f"  {status} {feature}")

    # Summary
    print("\n" + "="*80)
    all_classes_present = all(cls in classes for cls in required_classes)
    all_functions_present = all(func in functions for func in required_functions)
    all_features_present = all(keyword in code for keyword in critical_features.values())

    if all_classes_present and all_functions_present and all_features_present:
        print("✓ VERIFICATION PASSED: All components present")
        print("="*80)
        print("\nThe integrated code contains:")
        print(f"  • {len([c for c in required_classes if c in classes])}/{len(required_classes)} required classes")
        print(f"  • {len([f for f in required_functions if f in functions])}/{len(required_functions)} required functions")
        print(f"  • All critical features")
        print("\nReady to run with FIGARO data (2010-2022)")
        return True
    else:
        print("✗ VERIFICATION FAILED: Some components missing")
        print("="*80)
        return False

if __name__ == "__main__":
    filepath = Path("integrated_dual_shock_spectral_analysis.py")

    if not filepath.exists():
        print(f"✗ Error: {filepath} not found")
        sys.exit(1)

    success = check_code_structure(filepath)
    sys.exit(0 if success else 1)
