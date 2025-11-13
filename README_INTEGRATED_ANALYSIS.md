# Integrated Dual Shock Propagation with Spectral RMT Analysis

## Overview

This integrated framework combines dual shock propagation analysis (Leontief & Ghosh) with Random Matrix Theory (RMT) spectral filtering for comprehensive Input-Output network analysis of FIGARO data from 2010-2022.

## Features

✅ **Dual Shock Propagation**
- Leontief demand-side shocks (α·L·Δf)
- Ghosh supply-side shocks (β·G·Δv)
- Combined dual-shock framework

✅ **Random Matrix Theory (RMT) Analysis**
- Correlation-based spectral analysis
- Marchenko-Pastur bounds for signal/noise separation
- Eigenvalue outlier detection
- Eigenportfolio analysis

✅ **Policy Scenarios**
- Construction sector stimulus
- Energy crisis (supply shock)
- Pandemic (correlated demand+supply)
- Trade war (export collapse)

✅ **Temporal Analysis**
- Multi-year spectral evolution
- Kolmogorov-Smirnov tests for MP fit
- Systemic risk indicators
- Financial contagion detection

✅ **Network Visualization**
- **NO SELF-LOOPS** in all network plots
- Directed weighted graphs
- PageRank and centrality measures

## Required Data Files

For each year (2010-2022), you need three CSV files:

```
sector_only_matrix_{year}.csv           # Z matrix (intermediate flows)
final_demand_only_matrix_{year}.csv     # F matrix (final demand)
value_added_only_matrix_{year}.csv      # V matrix (value added)
```

Place these files in the same directory as the script.

## Output Files

### For Each Year (2010-2022):

**Directory structure:**
```
results/{year}/
  - figaro_shock_analysis_results.csv
  - figaro_sensitivity_analysis.csv
  - matrix_A_leontief.npy
  - matrix_B_ghosh.npy

figures/{year}/
  - plot_1_spectral_comparison.png
  - plot_2_sector_impact.png
  - plot_7_rmt_analysis.png
  - plot_8_sensitivity_analysis.png
```

### Temporal Analysis (All Years):

**Directory: results/**
```
- temporal_systemic_risk_indicators.csv
- kolmogorov_smirnov_tests.csv
- financial_contagion_analysis.csv
```

**Directory: figures/**
```
- plot_9_temporal_rmt_analysis.png
- plot_10_contagion_analysis.png
```

## Usage

### Basic Usage

```bash
python integrated_dual_shock_spectral_analysis.py
```

The script will:
1. Process each year (2010-2022) sequentially
2. Generate all CSV files and visualizations per year
3. Perform temporal RMT analysis across all years
4. Generate contagion analysis comparing first and last years

### Configuration

Edit the `CONFIG` dictionary at the top of the script:

```python
CONFIG = {
    'years': list(range(2010, 2023)),      # Years to analyze
    'data_dir': Path('.'),                  # Data directory
    'results_dir': Path('./results'),       # Results output
    'figures_dir': Path('./figures'),       # Figures output
    'top_k_sectors': 50,                    # Top sectors for viz
    'rmt_variance': 1.0,                    # RMT variance parameter
    'dual_shock_alpha': 0.6,                # Demand weight
    'dual_shock_beta': 0.4,                 # Supply weight
}
```

## Key Outputs Explained

### 1. figaro_shock_analysis_results.csv

Contains per-sector analysis:
- **Output**: Gross output (x)
- **Final_Demand**: Final demand (d)
- **Value_Added**: Value added (v)
- **Demand_Impact**: Δx from demand shock (L·Δf)
- **Supply_Impact**: Δx from supply shock (G·Δv)
- **Total_Impact**: Combined impact (α·Δx_demand + β·Δx_supply)
- **Impact_Percent**: Total impact as % of output
- **Backward_Linkages**: Sum of column of A matrix
- **Forward_Linkages**: Sum of row of A matrix

### 2. figaro_sensitivity_analysis.csv

Compares multiple policy scenarios:
- **Scenario**: Scenario name
- **Total_Change**: Aggregate output change
- **Demand_Contribution**: Contribution from demand side
- **Supply_Contribution**: Contribution from supply side
- **Max_Impact_Sector**: Sector with largest impact
- **Max_Impact_Value**: Value of maximum impact

### 3. temporal_systemic_risk_indicators.csv

Time-series of risk metrics:
- **Market_Mode**: Dominant eigenvalue (λ_max)
- **Turbulence_Index**: Deviation from Marchenko-Pastur bound
- **Absorption_Ratio**: Variance explained by top 5 eigenvalues
- **Shannon_Entropy**: Eigenvalue diversity measure
- **Outlier_Fraction**: Fraction of eigenvalues beyond MP bounds

### 4. kolmogorov_smirnov_tests.csv

Statistical tests for random matrix null hypothesis:
- **KS_Statistic**: Kolmogorov-Smirnov test statistic
- **P_Value**: Statistical significance
- **Interpretation**: 'Reject MP' or 'Cannot reject MP'

### 5. financial_contagion_analysis.csv

Comparison of crisis vs normal periods:
- **Contagion_Score**: Weighted combination of changes
- **Contagion_Level**: Categorical assessment
- **Market_Mode_Change_Pct**: % change in dominant eigenvalue
- **Absorption_Ratio_Change_Pct**: % change in concentration
- **Entropy_Change_Pct**: % change in diversity

### 6. Matrix Files (.npy)

NumPy arrays for further analysis:
- **matrix_A_leontief.npy**: Leontief technical coefficients (A)
- **matrix_B_ghosh.npy**: Ghosh allocation coefficients (B)

Load with: `A = np.load('matrix_A_leontief.npy')`

## Visualizations

### Plot 1: Spectral Comparison
- Left: Eigenvalues in complex plane (A vs B)
- Right: Magnitude distribution histogram
- **Interpretation**: Stability if all eigenvalues inside unit circle

### Plot 2: Sector Impact
- Horizontal bar chart of top 20 sectors
- Blue bars: Demand impact
- Red bars: Supply impact
- **Interpretation**: Identifies most affected sectors

### Plot 7: RMT Analysis
- Top-left: Eigenvalue spectrum vs Marchenko-Pastur
- Top-right: Outlier eigenvalues (signal)
- Bottom-left: Sector correlation strength
- Bottom-right: Correlation matrix heatmap
- **Interpretation**: Outliers = non-random structure

### Plot 8: Sensitivity Analysis
- Four panels comparing policy scenarios
- Total impact, demand vs supply, max sectoral impact, summary table
- **Interpretation**: Compares effectiveness of interventions

### Plot 9: Temporal RMT Analysis
- Evolution of spectral risk indicators over time
- Market mode, turbulence, absorption ratio, outlier fraction
- **Interpretation**: Tracks systemic risk over years

### Plot 10: Contagion Analysis
- Comparison of crisis vs normal period
- Contagion score gauge, metric changes, summary
- **Interpretation**: Quantifies financial contagion

## Technical Details

### IO System Fundamentals

**Leontief (Demand-Side):**
- Technical coefficients: A_ij = Z_ij / x_j
- Leontief inverse: L = (I - A)^(-1)
- Demand propagation: Δx = L·Δf

**Ghosh (Supply-Side):**
- Allocation coefficients: B_ij = Z_ij / x_i
- Ghosh inverse: G = (I - B)^(-1)
- Supply propagation: Δx = Δv·G

**Dual Shock:**
- Combined: Δx_total = α·(L·Δf) + β·(Δv·G)
- Default weights: α=0.6, β=0.4

### RMT Spectral Analysis

**Marchenko-Pastur Distribution:**
- Aspect ratio: λ = N/T (sectors/shocks)
- Bounds: λ_min = (1 - √λ)², λ_max = (1 + √λ)²
- Eigenvalues beyond λ_max = signal (non-random structure)

**Outlier Detection:**
- Signal: |eigenvalue| > λ_max
- Noise: |eigenvalue| ≤ λ_max
- Interpretation: Outliers indicate systemic connections

### Network Topology

**CRITICAL: NO SELF-LOOPS**
- All network visualizations exclude diagonal elements (i ≠ j)
- Ensures proper representation of inter-sectoral flows
- Self-production (Z_ii) not shown in network graphs

## Troubleshooting

### Issue: "File not found"
**Solution:** Ensure CSV files are named correctly:
```
sector_only_matrix_2010.csv
final_demand_only_matrix_2010.csv
value_added_only_matrix_2010.csv
```

### Issue: "Singular matrix" or "LinAlgError"
**Solution:** The code automatically uses pseudoinverse (pinv) for ill-conditioned matrices. Check diagnostics for condition numbers.

### Issue: "Insufficient data for temporal analysis"
**Solution:** Need at least 2 years of data. Check that data files exist for multiple years.

### Issue: Memory error with large matrices
**Solution:** Reduce `top_k_sectors` in CONFIG or process fewer years.

## Dependencies

```
numpy
pandas
scipy
matplotlib
seaborn
networkx
```

Install with:
```bash
pip install numpy pandas scipy matplotlib seaborn networkx
```

## Citation

If you use this code, please cite:

```bibtex
@software{integrated_dual_shock_rmt_2025,
  title={Integrated Dual Shock Propagation with Spectral RMT Analysis},
  author={Multi-Agent Analysis System},
  year={2025},
  version={3.0.0}
}
```

## References

1. **Leontief Input-Output Analysis:**
   - Miller, R. E., & Blair, P. D. (2009). *Input-Output Analysis: Foundations and Extensions*. Cambridge University Press.

2. **Ghosh Supply-Side Model:**
   - Ghosh, A. (1958). "Input-Output Approach in an Allocation System". *Economica*, 25(97), 58-64.

3. **Random Matrix Theory:**
   - Marčenko, V. A., & Pastur, L. A. (1967). "Distribution of eigenvalues for some sets of random matrices". *Mathematics of the USSR-Sbornik*, 1(4), 457.
   - Laloux, L., Cizeau, P., Bouchaud, J. P., & Potters, M. (1999). "Noise dressing of financial correlation matrices". *Physical Review Letters*, 83(7), 1467.

4. **FIGARO Database:**
   - Remond-Tiedrez, A., & Rueda-Cantuche, J. M. (2019). "EU inter-country supply, use and input-output tables—Full international and global accounts for research in input-output analysis (FIGARO)". *JRC Technical Reports*.

## License

MIT License - See LICENSE file for details.

## Support

For issues or questions:
1. Check this README thoroughly
2. Review the code documentation
3. Examine log output for specific errors
4. Check data file formats match FIGARO conventions

---

**Version:** 3.0.0 - Fully Integrated
**Last Updated:** 2025
**Status:** Production Ready
