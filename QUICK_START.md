# Quick Start Guide

## 1. Prerequisites

Ensure you have the required Python packages:

```bash
pip install numpy pandas scipy matplotlib seaborn networkx
```

## 2. Prepare Your Data

Place FIGARO CSV files in the current directory:

```
sector_only_matrix_2010.csv
final_demand_only_matrix_2010.csv
value_added_only_matrix_2010.csv

sector_only_matrix_2011.csv
final_demand_only_matrix_2011.csv
value_added_only_matrix_2011.csv

... (repeat for 2012-2022)
```

## 3. Run the Analysis

```bash
python integrated_dual_shock_spectral_analysis.py
```

## 4. Expected Runtime

- **Per year:** 2-5 minutes
- **Total (13 years):** 30-60 minutes
- Depends on: number of sectors, CPU speed, disk I/O

## 5. Check Outputs

### Per-year results (in `results/YYYY/`):

```bash
ls results/2010/
# figaro_shock_analysis_results.csv
# figaro_sensitivity_analysis.csv
# matrix_A_leontief.npy
# matrix_B_ghosh.npy
```

### Per-year figures (in `figures/YYYY/`):

```bash
ls figures/2010/
# plot_1_spectral_comparison.png
# plot_2_sector_impact.png
# plot_7_rmt_analysis.png
# plot_8_sensitivity_analysis.png
```

### Temporal analysis (in `results/` and `figures/`):

```bash
ls results/
# temporal_systemic_risk_indicators.csv
# kolmogorov_smirnov_tests.csv
# financial_contagion_analysis.csv

ls figures/
# plot_9_temporal_rmt_analysis.png
# plot_10_contagion_analysis.png
```

## 6. Interpret Results

### Key CSV Files to Check First:

1. **`figaro_shock_analysis_results.csv`** - Sector-level impacts
   - Sort by `Total_Impact` (descending) to find most affected sectors
   - Check `Impact_Percent` for relative impacts

2. **`figaro_sensitivity_analysis.csv`** - Scenario comparison
   - Compare `Total_Change` across scenarios
   - Identify which policy has largest effect

3. **`temporal_systemic_risk_indicators.csv`** - Risk over time
   - Plot `Turbulence_Index` to see crisis periods
   - High `Outlier_Fraction` = more systemic structure

4. **`financial_contagion_analysis.csv`** - Crisis assessment
   - `Contagion_Score` > 50 = severe contagion
   - Check individual metric changes

### Key Visualizations:

1. **Plot 1** - Check if eigenvalues inside unit circle (stability)
2. **Plot 2** - Identify most vulnerable sectors
3. **Plot 7** - See if structure is random (eigenvalues follow MP)
4. **Plot 9** - Track risk evolution over time
5. **Plot 10** - Quantify contagion between periods

## 7. Customize Analysis

Edit `CONFIG` dictionary in the script:

```python
CONFIG = {
    'years': list(range(2010, 2023)),      # Change years
    'dual_shock_alpha': 0.6,                # Demand weight
    'dual_shock_beta': 0.4,                 # Supply weight
    'top_k_sectors': 50,                    # Number of top sectors
    'rmt_variance': 1.0,                    # RMT parameter
}
```

## 8. Troubleshooting

### Problem: "File not found"
**Solution:** Check file naming matches exactly:
```bash
ls sector_only_matrix_*.csv
ls final_demand_only_matrix_*.csv
ls value_added_only_matrix_*.csv
```

### Problem: Script runs but no outputs
**Solution:** Check log messages - may be skipping years due to missing data

### Problem: "Singular matrix" warnings
**Solution:** Normal - code uses pseudoinverse automatically for ill-conditioned cases

### Problem: Out of memory
**Solution:** Reduce `top_k_sectors` or process fewer years

## 9. Verify Installation

Run verification script first:

```bash
python verify_integration.py
```

Should show:
```
✓ VERIFICATION PASSED: All components present
```

## 10. Next Steps

1. **Explore Results:** Open CSV files in Excel/Python
2. **Visualize:** View PNG files to understand patterns
3. **Deep Dive:** Focus on years/sectors of interest
4. **Compare:** Contrast pre-crisis vs crisis periods
5. **Export:** Use results for reports/papers

## Example Analysis Workflow

```bash
# 1. Verify code
python verify_integration.py

# 2. Run analysis
python integrated_dual_shock_spectral_analysis.py

# 3. Check specific year
cat results/2020/figaro_shock_analysis_results.csv | head -20

# 4. View temporal trends
python -c "
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('results/temporal_systemic_risk_indicators.csv')
plt.plot(df['Period'], df['Turbulence_Index'])
plt.title('Turbulence Over Time')
plt.xlabel('Year')
plt.ylabel('Turbulence Index')
plt.savefig('turbulence_trend.png')
"

# 5. Compare scenarios
python -c "
import pandas as pd

df = pd.read_csv('results/2020/figaro_sensitivity_analysis.csv')
print(df.sort_values('Total_Change', ascending=False))
"
```

## Support

For detailed documentation, see `README_INTEGRATED_ANALYSIS.md`

For technical questions:
1. Check the comprehensive README
2. Review code comments
3. Examine log output for specific errors
4. Verify data file formats

---

**Quick Reference:**

| File | Purpose |
|------|---------|
| `integrated_dual_shock_spectral_analysis.py` | Main analysis script |
| `verify_integration.py` | Verification tool |
| `README_INTEGRATED_ANALYSIS.md` | Full documentation |
| `QUICK_START.md` | This file |

**Status:** ✓ Production Ready | **Version:** 3.0.0
