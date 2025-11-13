"""
================================================================================
INTEGRATED DUAL SHOCK PROPAGATION WITH SPECTRAL RMT ANALYSIS
Production Networks (FIGARO 2010-2022)
Complete Implementation - All Outputs Generated

This integrated framework combines:
  ✓ Dual shock propagation (Leontief & Ghosh)
  ✓ Random Matrix Theory (RMT) filtering
  ✓ Temporal spectral analysis
  ✓ Policy scenario analysis
  ✓ Sensitivity analysis
  ✓ Network visualizations (NO self-loops)
  ✓ Financial contagion detection
  ✓ Complete CSV and visualization outputs

Outputs for each year (2010-2022):
  CSV Files:
    - figaro_shock_analysis_results.csv
    - figaro_sensitivity_analysis.csv
    - temporal_systemic_risk_indicators.csv
    - kolmogorov_smirnov_tests.csv
    - financial_contagion_analysis.csv

  Matrix Files:
    - matrix_A_leontief.npy
    - matrix_B_ghosh.npy

  Visualizations:
    - plot_1_spectral_comparison.png
    - plot_2_sector_impact.png
    - plot_7_rmt_analysis.png
    - plot_8_sensitivity_analysis.png
    - plot_9_temporal_rmt_analysis.png
    - plot_10_contagion_analysis.png

Author: Multi-Agent Analysis System
Date: 2025
Version: 3.0.0 - Fully Integrated
================================================================================
"""

import numpy as np
import pandas as pd
import scipy
from scipy import linalg, sparse, stats
from scipy.sparse.linalg import eigs, eigsh
from scipy.stats import spearmanr
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import seaborn as sns
import networkx as nx
from pathlib import Path
import json
import logging
from typing import Dict, Tuple, List, Optional, Union
from dataclasses import dataclass
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings('ignore')

# Set random seed
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Numerical tolerances
TOLERANCE = 1e-10
COND_THRESHOLD_PINV = 1e10

# Configuration
CONFIG = {
    'years': list(range(2010, 2023)),
    'data_dir': Path('.'),
    'results_dir': Path('./results'),
    'figures_dir': Path('./figures'),
    'top_k_sectors': 50,
    'pagerank_damping_prob': 0.15,
    'rmt_variance': 1.0,
    'shock_scenarios': ['construction_stimulus', 'energy_crisis', 'pandemic', 'trade_war'],
    'dual_shock_alpha': 0.6,  # Demand weight
    'dual_shock_beta': 0.4,   # Supply weight
}

# Create output directories
CONFIG['results_dir'].mkdir(exist_ok=True)
CONFIG['figures_dir'].mkdir(exist_ok=True)

# Color scheme
COLORS = {
    'primary_blue': '#377eb8',
    'primary_red': '#e41a1c',
    'primary_green': '#4daf4a',
    'demand': '#4575b4',
    'supply': '#d73027',
    'leontief': '#377eb8',
    'ghosh': '#e41a1c'
}

logger.info("="*80)
logger.info("INTEGRATED DUAL SHOCK PROPAGATION WITH SPECTRAL RMT ANALYSIS")
logger.info("="*80)


# ============================================================================
# SECTION 1: IO SYSTEM
# ============================================================================

class IOSystem:
    """Input-Output Economic System with Leontief and Ghosh frameworks."""

    def __init__(self, Z: np.ndarray, x: np.ndarray, d: np.ndarray, v: np.ndarray):
        """Initialize IO system from fundamental matrices and vectors."""
        self.n = len(x)
        self.Z = Z.copy()
        self.x = x.copy()
        self.d = d.copy()
        self.v = v.copy()

        self.diagnostics = {}

        self._validate_dimensions()
        self.A = self._compute_leontief_coefficients()
        self.B = self._compute_ghosh_coefficients()
        self.L = None
        self.G = None
        self._compute_inverses()

    def _validate_dimensions(self):
        """Validate dimensions."""
        if self.Z.shape != (self.n, self.n):
            raise ValueError(f"Z must be ({self.n}, {self.n})")
        if len(self.d) != self.n or len(self.v) != self.n:
            raise ValueError(f"Vectors must have length {self.n}")

    def _compute_leontief_coefficients(self) -> np.ndarray:
        """Compute Leontief technical coefficients: A_ij = Z_ij / x_j"""
        A = np.zeros((self.n, self.n))
        for j in range(self.n):
            if self.x[j] > TOLERANCE:
                A[:, j] = self.Z[:, j] / self.x[j]
        return A

    def _compute_ghosh_coefficients(self) -> np.ndarray:
        """Compute Ghosh allocation coefficients: B_ij = Z_ij / x_i"""
        B = np.zeros((self.n, self.n))
        for i in range(self.n):
            if self.x[i] > TOLERANCE:
                B[i, :] = self.Z[i, :] / self.x[i]
        return B

    def _compute_inverses(self):
        """Compute Leontief and Ghosh inverse matrices."""
        I = np.eye(self.n)

        # Leontief inverse
        try:
            I_minus_A = I - self.A
            cond_IA = np.linalg.cond(I_minus_A)
            self.diagnostics['cond_I_minus_A'] = cond_IA

            if cond_IA > COND_THRESHOLD_PINV:
                self.L = linalg.pinv(I_minus_A, rcond=TOLERANCE)
                self.diagnostics['leontief_used_pinv'] = True
            else:
                self.L = linalg.inv(I_minus_A)
                self.diagnostics['leontief_used_pinv'] = False
        except linalg.LinAlgError:
            self.L = linalg.pinv(I - self.A, rcond=TOLERANCE)
            self.diagnostics['leontief_used_pinv'] = True

        # Ghosh inverse
        try:
            I_minus_B = I - self.B
            cond_IB = np.linalg.cond(I_minus_B)
            self.diagnostics['cond_I_minus_B'] = cond_IB

            if cond_IB > COND_THRESHOLD_PINV:
                self.G = linalg.pinv(I_minus_B, rcond=TOLERANCE)
                self.diagnostics['ghosh_used_pinv'] = True
            else:
                self.G = linalg.inv(I_minus_B)
                self.diagnostics['ghosh_used_pinv'] = False
        except linalg.LinAlgError:
            self.G = linalg.pinv(I - self.B, rcond=TOLERANCE)
            self.diagnostics['ghosh_used_pinv'] = True

        # Spectral radii
        self.diagnostics['rho_A'] = np.max(np.abs(np.linalg.eigvals(self.A)))
        self.diagnostics['rho_B'] = np.max(np.abs(np.linalg.eigvals(self.B)))


# ============================================================================
# SECTION 2: SHOCK GENERATION AND PROPAGATION
# ============================================================================

class ShockGenerator:
    """Generates demand and supply shocks."""

    def __init__(self, n: int, seed: Optional[int] = RANDOM_SEED):
        self.n = n
        self.rng = np.random.default_rng(seed)

    def generate_demand_shock(self, shock_type: str, params: Dict) -> np.ndarray:
        """Generate demand shock vector."""
        if shock_type == 'sector_specific':
            shock = np.zeros(self.n)
            sectors = params.get('sectors', [0])
            magnitude = params.get('magnitude', 0.1)
            for sector in sectors:
                if 0 <= sector < self.n:
                    shock[sector] = magnitude
            return shock
        elif shock_type == 'random_correlated':
            mean = params.get('mean', 0.0)
            std = params.get('std', 0.1)
            correlation = params.get('correlation', 0.5)
            common_factor = self.rng.normal(0, 1)
            idiosyncratic = self.rng.normal(0, 1, self.n)
            shock = mean + std * (np.sqrt(correlation) * common_factor +
                                 np.sqrt(1 - correlation) * idiosyncratic)
            return shock
        else:
            raise ValueError(f"Unknown shock type: {shock_type}")

    def generate_demand_shock_matrix(self, shock_type: str, params: Dict) -> np.ndarray:
        """Generate demand shock matrix for multiple shocks."""
        n_shocks = params.get('n_shocks', self.n)
        shock_matrix = np.zeros((self.n, n_shocks))
        for i in range(n_shocks):
            shock_matrix[:, i] = self.generate_demand_shock(shock_type, params)
        return shock_matrix


class ShockPropagator:
    """Propagates shocks through the IO system."""

    def __init__(self, io_system: IOSystem):
        self.io_system = io_system

    def propagate_demand_shock(self, delta_f: np.ndarray) -> Dict:
        """Propagate demand shock: Δx = L @ Δf"""
        delta_x = self.io_system.L @ delta_f
        total_change = np.sum(delta_x)
        max_impact_idx = np.argmax(np.abs(delta_x))

        return {
            'delta_x': delta_x,
            'total_change': total_change,
            'max_impact_sector': max_impact_idx,
            'max_impact_value': delta_x[max_impact_idx]
        }

    def propagate_supply_shock(self, delta_v: np.ndarray) -> Dict:
        """Propagate supply shock: Δx' = Δv @ G"""
        delta_x_prime = delta_v @ self.io_system.G
        total_change = np.sum(delta_x_prime)
        max_impact_idx = np.argmax(np.abs(delta_x_prime))

        return {
            'delta_x_prime': delta_x_prime,
            'total_change': total_change,
            'max_impact_sector': max_impact_idx,
            'max_impact_value': delta_x_prime[max_impact_idx]
        }

    def propagate_dual_shock(self, delta_f: np.ndarray, delta_v: np.ndarray,
                            alpha: float, beta: float) -> Dict:
        """Propagate combined demand and supply shock: α·Δx + β·Δx'"""
        demand_results = self.propagate_demand_shock(delta_f)
        supply_results = self.propagate_supply_shock(delta_v)

        delta_x_demand = demand_results['delta_x']
        delta_x_supply = supply_results['delta_x_prime']
        delta_x_total = alpha * delta_x_demand + beta * delta_x_supply

        total_change = np.sum(delta_x_total)
        max_impact_idx = np.argmax(np.abs(delta_x_total))

        return {
            'delta_x_total': delta_x_total,
            'delta_x_demand': delta_x_demand,
            'delta_x_supply': delta_x_supply,
            'total_change': total_change,
            'demand_contribution': alpha * np.sum(delta_x_demand),
            'supply_contribution': beta * np.sum(delta_x_supply),
            'max_impact_sector': max_impact_idx,
            'max_impact_value': delta_x_total[max_impact_idx]
        }


# ============================================================================
# SECTION 3: POLICY SHOCK SCENARIOS
# ============================================================================

def identify_policy_sectors(sector_labels):
    """Identify sectors relevant to policy scenarios."""
    construction_keywords = ['construction', 'real estate', 'building', 'dwelling']
    energy_keywords = ['electricity', 'gas', 'energy', 'fuel', 'power']

    construction_idx = [i for i, s in enumerate(sector_labels)
                        if any(k in s.lower() for k in construction_keywords)]
    energy_idx = [i for i, s in enumerate(sector_labels)
                if any(k in s.lower() for k in energy_keywords)]

    return construction_idx, energy_idx


def generate_policy_shocks(shock_gen, n_sectors, sector_labels):
    """Generate policy-relevant shock scenarios."""
    construction_idx, energy_idx = identify_policy_sectors(sector_labels)

    scenarios = {}

    # SCENARIO 1: Construction Sector Stimulus
    if construction_idx:
        delta_f_construction = np.zeros(n_sectors)
        for idx in construction_idx:
            delta_f_construction[idx] = 1000.0
        scenarios['construction_stimulus'] = {
            'name': 'Construction Sector Demand Stimulus',
            'delta_f': delta_f_construction,
            'delta_v': np.zeros(n_sectors),
            'alpha': 1.0,
            'beta': 0.0,
            'description': f'Boost to {len(construction_idx)} construction sectors'
        }

    # SCENARIO 2: Energy Crisis
    if energy_idx:
        delta_v_energy = np.zeros(n_sectors)
        for idx in energy_idx:
            delta_v_energy[idx] = -500.0
        scenarios['energy_crisis'] = {
            'name': 'Energy Sector Supply Crisis',
            'delta_f': np.zeros(n_sectors),
            'delta_v': delta_v_energy,
            'alpha': 0.0,
            'beta': 1.0,
            'description': f'Supply reduction in {len(energy_idx)} energy sectors'
        }

    # SCENARIO 3: Pandemic
    delta_f_pandemic = shock_gen.generate_demand_shock(
        'random_correlated',
        {'mean': -200.0, 'std': 100.0, 'correlation': 0.7}
    )
    delta_v_pandemic = shock_gen.generate_demand_shock(
        'random_correlated',
        {'mean': -100.0, 'std': 50.0, 'correlation': 0.7}
    )
    scenarios['pandemic'] = {
        'name': 'Pandemic Shock (Demand + Supply)',
        'delta_f': delta_f_pandemic,
        'delta_v': delta_v_pandemic,
        'alpha': 0.6,
        'beta': 0.4,
        'description': 'Correlated demand and supply reduction'
    }

    # SCENARIO 4: Trade War
    delta_f_trade = shock_gen.generate_demand_shock(
        'random_correlated',
        {'mean': -150.0, 'std': 80.0, 'correlation': 0.5}
    )
    scenarios['trade_war'] = {
        'name': 'Trade War / Export Collapse',
        'delta_f': delta_f_trade,
        'delta_v': np.zeros(n_sectors),
        'alpha': 1.0,
        'beta': 0.0,
        'description': 'Export demand reduction'
    }

    return scenarios


def conduct_sensitivity_analysis(propagator, sector_labels, scenarios):
    """Conduct sensitivity analysis across scenarios."""
    sensitivity_results = {}

    for scenario_name, scenario in scenarios.items():
        results = propagator.propagate_dual_shock(
            scenario['delta_f'],
            scenario['delta_v'],
            alpha=scenario['alpha'],
            beta=scenario['beta']
        )

        sensitivity_results[scenario_name] = {
            'name': scenario['name'],
            'description': scenario['description'],
            'total_change': results['total_change'],
            'demand_contribution': results['demand_contribution'],
            'supply_contribution': results['supply_contribution'],
            'max_impact_sector': sector_labels[results['max_impact_sector']],
            'max_impact_value': results['max_impact_value'],
            'delta_x': results['delta_x_total']
        }

    return sensitivity_results


# ============================================================================
# SECTION 4: RMT SPECTRAL ANALYSIS
# ============================================================================

class EnhancedSpectralAnalyzer:
    """RMT analysis using correlation matrices."""

    def __init__(self, raw_shock_matrix: np.ndarray, correlation_method: str = 'pearson'):
        self.raw_matrix = raw_shock_matrix
        self.n_sectors, self.n_shocks = raw_shock_matrix.shape
        self.correlation_method = correlation_method

        self.correlation_matrix = self._compute_correlation_matrix()
        self.eigenvalues = None
        self.eigenvectors = None

    def _compute_correlation_matrix(self) -> np.ndarray:
        """Compute correlation matrix."""
        if self.correlation_method == 'pearson':
            return np.corrcoef(self.raw_matrix)
        elif self.correlation_method == 'spearman':
            n = self.raw_matrix.shape[0]
            C = np.zeros((n, n))
            for i in range(n):
                for j in range(i, n):
                    rho, _ = spearmanr(self.raw_matrix[i], self.raw_matrix[j])
                    C[i, j] = rho
                    C[j, i] = rho
            return C
        else:
            raise ValueError("correlation_method must be 'pearson' or 'spearman'")

    def compute_spectrum(self) -> dict:
        """Compute eigenvalue spectrum."""
        eigenvalues, eigenvectors = linalg.eigh(self.correlation_matrix)

        sorted_idx = np.argsort(np.abs(eigenvalues))[::-1]
        self.eigenvalues = eigenvalues[sorted_idx]
        self.eigenvectors = eigenvectors[:, sorted_idx]

        spectral_radius = np.max(np.abs(self.eigenvalues))

        return {
            'eigenvalues': self.eigenvalues,
            'eigenvectors': self.eigenvectors,
            'spectral_radius': spectral_radius,
            'correlation_matrix': self.correlation_matrix
        }

    def marchenko_pastur_bounds(self, variance: float = 1.0) -> dict:
        """Calculate Marchenko-Pastur bounds."""
        lambda_param = self.n_sectors / self.n_shocks

        if lambda_param <= 1:
            sqrt_term = np.sqrt(lambda_param)
        else:
            sqrt_term = np.sqrt(1 / lambda_param)

        lambda_min = variance * (1 - sqrt_term)**2
        lambda_max = variance * (1 + sqrt_term)**2

        return {
            'lambda_param': lambda_param,
            'lambda_min': lambda_min,
            'lambda_max': lambda_max,
            'x_range': np.linspace(0, lambda_max * 1.2, 500)
        }

    def marchenko_pastur_pdf(self, x_range: np.ndarray, variance: float = 1.0) -> np.ndarray:
        """Compute Marchenko-Pastur PDF."""
        bounds = self.marchenko_pastur_bounds(variance)
        lambda_param = bounds['lambda_param']
        lambda_min = bounds['lambda_min']
        lambda_max = bounds['lambda_max']

        pdf = np.zeros_like(x_range)

        for i, x in enumerate(x_range):
            if lambda_min <= x <= lambda_max and x > 0:
                numerator = np.sqrt((lambda_max - x) * (x - lambda_min))

                if lambda_param <= 1:
                    denominator = 2 * np.pi * variance * x * lambda_param
                else:
                    denominator = 2 * np.pi * variance * x / lambda_param

                pdf[i] = numerator / denominator if denominator > TOLERANCE else 0

        return pdf

    def identify_outliers(self, variance: float = 1.0) -> dict:
        """Identify eigenvalues beyond MP bounds."""
        if self.eigenvalues is None:
            self.compute_spectrum()

        bounds = self.marchenko_pastur_bounds(variance)
        lambda_max = bounds['lambda_max']

        abs_eigenvalues = np.abs(self.eigenvalues)
        outlier_mask = abs_eigenvalues > lambda_max
        outlier_indices = np.where(outlier_mask)[0]

        return {
            'lambda_max': lambda_max,
            'n_outliers': len(outlier_indices),
            'outlier_indices': outlier_indices,
            'outlier_eigenvalues': self.eigenvalues[outlier_mask],
            'outlier_mask': outlier_mask
        }

    def sector_correlation_strength(self) -> np.ndarray:
        """Compute average correlation strength per sector."""
        C = self.correlation_matrix
        n = C.shape[0]

        correlation_strength = np.zeros(n)
        for i in range(n):
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            correlation_strength[i] = np.mean(np.abs(C[i, mask]))

        return correlation_strength

    def compute_eigenportfolios(self, n_portfolios: int = 5) -> dict:
        """Compute eigenportfolios."""
        if self.eigenvectors is None:
            self.compute_spectrum()

        eigenportfolios = {}
        for i in range(min(n_portfolios, len(self.eigenvalues))):
            eigenportfolios[f'EP_{i+1}'] = {
                'weights': self.eigenvectors[:, i],
                'eigenvalue': self.eigenvalues[i],
                'variance_explained': self.eigenvalues[i] / np.sum(np.abs(self.eigenvalues))
            }

        return eigenportfolios


class TemporalRMTAnalyzer:
    """Analyze spectral properties across time periods."""

    def __init__(self, shock_matrices_dict: dict, sector_labels: List[str], variance: float = 1.0):
        self.periods = list(shock_matrices_dict.keys())
        self.shock_matrices = shock_matrices_dict
        self.sector_labels = sector_labels
        self.variance = variance

        self.analyzers = {}
        self.spectra = {}
        self.outliers = {}

        for period, matrix in shock_matrices_dict.items():
            analyzer = EnhancedSpectralAnalyzer(matrix, correlation_method='pearson')
            self.analyzers[period] = analyzer
            self.spectra[period] = analyzer.compute_spectrum()
            self.outliers[period] = analyzer.identify_outliers(variance)

    def kolmogorov_smirnov_test(self, period: str) -> dict:
        """Perform KS test for MP fit."""
        analyzer = self.analyzers[period]
        spectrum = self.spectra[period]
        eigenvalues = np.abs(spectrum['eigenvalues'])

        bounds = analyzer.marchenko_pastur_bounds(self.variance)
        lambda_min = bounds['lambda_min']
        lambda_max = bounds['lambda_max']
        lambda_param = bounds['lambda_param']

        eigs_in_support = eigenvalues[(eigenvalues >= lambda_min) & (eigenvalues <= lambda_max)]

        if len(eigs_in_support) < 10:
            return {
                'ks_statistic': np.nan,
                'p_value': np.nan,
                'significant': False,
                'interpretation': 'Insufficient data',
                'n_eigenvalues_tested': len(eigs_in_support),
                'lambda_param': lambda_param
            }

        x_range = np.linspace(lambda_min, lambda_max, 1000)
        mp_density = analyzer.marchenko_pastur_pdf(x_range, self.variance)
        mp_cdf = np.cumsum(mp_density) * (x_range[1] - x_range[0])
        mp_cdf = mp_cdf / (mp_cdf[-1] + 1e-10)

        def mp_cdf_func(x):
            x_norm = (x - lambda_min) / (lambda_max - lambda_min + 1e-10)
            return np.interp(x_norm, np.linspace(0, 1, len(mp_cdf)), mp_cdf)

        ks_stat, p_value = stats.kstest(eigs_in_support, mp_cdf_func)

        return {
            'ks_statistic': ks_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'interpretation': 'Reject MP' if p_value < 0.05 else 'Cannot reject MP',
            'n_eigenvalues_tested': len(eigs_in_support),
            'lambda_param': lambda_param
        }

    def compute_systemic_risk_indicators(self, period: str) -> dict:
        """Compute systemic risk indicators."""
        spectrum = self.spectra[period]
        eigenvalues = np.abs(spectrum['eigenvalues'])
        outliers = self.outliers[period]

        market_mode = eigenvalues.max()

        eigs_normalized = eigenvalues / eigenvalues.sum()
        shannon_entropy = -np.sum(eigs_normalized * np.log(eigs_normalized + 1e-10))

        outlier_fraction = outliers['n_outliers'] / len(eigenvalues)

        sorted_eigs = np.sort(eigenvalues)[::-1]
        spectral_gap = sorted_eigs[0] - sorted_eigs[1] if len(sorted_eigs) > 1 else 0

        absorption_ratio = sorted_eigs[:5].sum() / eigenvalues.sum()

        matrix = self.shock_matrices[period]
        n_sectors, n_shocks = matrix.shape
        lambda_param = n_sectors / n_shocks
        mp_upper = self.variance * (1 + np.sqrt(1/lambda_param))**2
        turbulence_index = (market_mode - mp_upper) / mp_upper

        return {
            'market_mode': market_mode,
            'shannon_entropy': shannon_entropy,
            'outlier_fraction': outlier_fraction,
            'spectral_gap': spectral_gap,
            'absorption_ratio': absorption_ratio,
            'turbulence_index': turbulence_index,
            'mp_upper_bound': mp_upper
        }

    def detect_financial_contagion(self, crisis_period: str, normal_period: str) -> dict:
        """Detect contagion by comparing spectral properties."""
        crisis_risk = self.compute_systemic_risk_indicators(crisis_period)
        normal_risk = self.compute_systemic_risk_indicators(normal_period)

        market_mode_change = ((crisis_risk['market_mode'] - normal_risk['market_mode']) /
                             normal_risk['market_mode'] * 100)

        outlier_change = ((crisis_risk['outlier_fraction'] - normal_risk['outlier_fraction']) /
                         (normal_risk['outlier_fraction'] + 1e-10) * 100)

        absorption_change = ((crisis_risk['absorption_ratio'] - normal_risk['absorption_ratio']) /
                            normal_risk['absorption_ratio'] * 100)

        entropy_change = ((crisis_risk['shannon_entropy'] - normal_risk['shannon_entropy']) /
                         normal_risk['shannon_entropy'] * 100)

        contagion_score = (
            0.4 * market_mode_change +
            0.3 * absorption_change +
            0.2 * outlier_change +
            0.1 * (-entropy_change)
        )

        if contagion_score > 50:
            contagion_level = 'Severe Contagion'
        elif contagion_score > 20:
            contagion_level = 'Moderate Contagion'
        elif contagion_score > 5:
            contagion_level = 'Mild Contagion'
        else:
            contagion_level = 'No Significant Contagion'

        return {
            'contagion_score': contagion_score,
            'contagion_level': contagion_level,
            'market_mode_change_pct': market_mode_change,
            'outlier_fraction_change_pct': outlier_change,
            'absorption_ratio_change_pct': absorption_change,
            'entropy_change_pct': entropy_change,
            'crisis_metrics': crisis_risk,
            'normal_metrics': normal_risk
        }


# ============================================================================
# SECTION 5: NETWORK VISUALIZER (NO SELF-LOOPS)
# ============================================================================

class NetworkVisualizer:
    """Network visualization for IO systems. NO SELF-LOOPS."""

    def __init__(self, io_system, sector_labels: List[str]):
        self.io_system = io_system
        self.sector_labels = sector_labels
        self.n = len(sector_labels)

    def _create_graph_no_selfloops(self, matrix: np.ndarray, threshold: float = 0.0) -> nx.DiGraph:
        """Create directed graph WITHOUT self-loops."""
        G = nx.DiGraph()

        for i in range(self.n):
            G.add_node(i, label=self.sector_labels[i])

        # CRITICAL: Exclude diagonal (i != j)
        for i in range(self.n):
            for j in range(self.n):
                if i != j and matrix[i, j] > threshold:
                    G.add_edge(i, j, weight=matrix[i, j])

        # Verify no self-loops
        assert all(u != v for u, v in G.edges()), "ERROR: Self-loops detected!"

        return G

    def plot_network_graph(self, matrix_type: str = 'A', threshold: float = 0.01,
                          top_n: int = 50, save_path: Optional[Path] = None):
        """Plot network graph WITHOUT self-loops."""
        matrix = self.io_system.A if matrix_type == 'A' else self.io_system.B
        G = self._create_graph_no_selfloops(matrix, threshold)

        # Filter to top N
        if G.number_of_nodes() > top_n:
            degrees = dict(G.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
            G = G.subgraph([n[0] for n in top_nodes]).copy()

        fig, ax = plt.subplots(figsize=(16, 16))

        pos = nx.spring_layout(G, k=2/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)

        node_metric = dict(G.degree())
        node_sizes = [200 + 1800 * (node_metric.get(node, 0) /
                     (max(node_metric.values()) + 1e-10)) for node in G.nodes()]
        node_colors = [node_metric.get(node, 0) for node in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors,
                              cmap=plt.cm.viridis, alpha=0.8, linewidths=2,
                              edgecolors='black', ax=ax)

        edge_weights = [data['weight'] for _, _, data in G.edges(data=True)]
        if edge_weights:
            edge_widths = 0.5 + 4.5 * np.array(edge_weights) / max(edge_weights)
            nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_weights,
                                  edge_cmap=plt.cm.plasma, alpha=0.6, arrows=True,
                                  arrowsize=20, connectionstyle='arc3,rad=0.15', ax=ax)

        labels = {node: self.sector_labels[node][:15] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                               font_weight='bold', font_color='white', ax=ax)

        title = f"Network Graph: {matrix_type} Matrix (NO Self-Loops)\n"
        title += f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            return fig


# ============================================================================
# SECTION 6: VISUALIZATION FUNCTIONS
# ============================================================================

def plot_spectral_comparison(A_props, B_props, save_path):
    """Plot 1: Spectral comparison of A and B."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    A_eigs = A_props['eigenvalues']
    B_eigs = B_props['eigenvalues']

    ax1.scatter(A_eigs.real, A_eigs.imag, alpha=0.6, s=50, color='blue', label='A')
    ax1.scatter(B_eigs.real, B_eigs.imag, alpha=0.6, s=50, color='red', label='B')

    theta = np.linspace(0, 2*np.pi, 100)
    ax1.plot(np.cos(theta), np.sin(theta), 'k--', linewidth=1, alpha=0.5)

    ax1.set_xlabel('Real Part', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Imaginary Part', fontsize=11, fontweight='bold')
    ax1.set_title('Eigenvalues in Complex Plane', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    A_abs = np.abs(A_eigs)
    B_abs = np.abs(B_eigs)

    ax2.hist(A_abs, bins=20, alpha=0.6, color='blue', label='A', edgecolor='black')
    ax2.hist(B_abs, bins=20, alpha=0.6, color='red', label='B', edgecolor='black')
    ax2.axvline(x=1, color='k', linestyle='--', linewidth=2)
    ax2.set_xlabel('Eigenvalue Magnitude', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax2.set_title('Eigenvalue Magnitude Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_sector_impact(sector_labels, results, save_path, top_n=20):
    """Plot 2: Top sectors by shock impact."""
    impacts_abs = np.abs(results['delta_x_total'])
    top_idx = np.argsort(impacts_abs)[::-1][:top_n]

    x_labels = [sector_labels[i] for i in top_idx]
    demand_vals = results['delta_x_demand'][top_idx]
    supply_vals = results['delta_x_supply'][top_idx]

    fig, ax = plt.subplots(figsize=(12, 8))

    x = np.arange(len(x_labels))
    width = 0.35

    ax.barh(x - width/2, demand_vals, width, label='Demand Impact',
           color='cornflowerblue', alpha=0.8)
    ax.barh(x + width/2, supply_vals, width, label='Supply Impact',
           color='coral', alpha=0.8)

    ax.set_yticks(x)
    ax.set_yticklabels(x_labels, fontsize=9)
    ax.set_xlabel('Output Change', fontsize=11, fontweight='bold')
    ax.set_title(f'Top {top_n} Sectors by Dual Shock Impact', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='x')
    ax.axvline(x=0, color='black', linewidth=0.8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_rmt_analysis(shock_matrix, sector_labels, save_path, top_n=50):
    """Plot 7: RMT Analysis."""
    analyzer = EnhancedSpectralAnalyzer(shock_matrix, correlation_method='pearson')
    spectrum = analyzer.compute_spectrum()
    bounds = analyzer.marchenko_pastur_bounds()
    outliers = analyzer.identify_outliers()
    correlation_strength = analyzer.sector_correlation_strength()

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 11))

    # Plot 1: Eigenvalue Distribution
    abs_eigenvalues = np.abs(spectrum['eigenvalues'])

    ax1.hist(abs_eigenvalues, bins=40, density=True, alpha=0.7,
            color='steelblue', label='Empirical', edgecolor='black')

    mp_pdf = analyzer.marchenko_pastur_pdf(bounds['x_range'])
    ax1.plot(bounds['x_range'], mp_pdf, 'r-', linewidth=2.5,
            label=f'Marchenko-Pastur (λ={bounds["lambda_param"]:.3f})')

    ax1.axvline(x=bounds['lambda_max'], color='green', linestyle='--',
               linewidth=2, label=f'λ_max={bounds["lambda_max"]:.3f}')

    ax1.set_xlabel('Eigenvalue', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Density', fontsize=11, fontweight='bold')
    ax1.set_title('Eigenvalue Spectrum vs Marchenko-Pastur', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Outliers
    if outliers['n_outliers'] > 0:
        outlier_eigs = np.abs(outliers['outlier_eigenvalues'])
        sorted_outliers = np.sort(outlier_eigs)[::-1]

        colors = ['red' if i == 0 else 'darkred' for i in range(len(sorted_outliers))]
        ax2.barh(range(len(sorted_outliers)), sorted_outliers, color=colors,
                alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Eigenvalue', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Outlier Rank', fontsize=11, fontweight='bold')
        ax2.set_title(f'{outliers["n_outliers"]} Outlier Eigenvalues', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
    else:
        ax2.text(0.5, 0.5, 'No outliers detected', ha='center', va='center',
                fontsize=12, transform=ax2.transAxes)
        ax2.axis('off')

    # Plot 3: Sector Correlation Strength
    top_corr_idx = np.argsort(correlation_strength)[::-1][:top_n]

    ax3.barh(range(top_n), correlation_strength[top_corr_idx],
            color='darkblue', alpha=0.7, edgecolor='black')
    ax3.set_yticks(range(top_n))
    ax3.set_yticklabels([sector_labels[i][:30] for i in top_corr_idx], fontsize=9)
    ax3.set_xlabel('Average Correlation Strength', fontsize=11, fontweight='bold')
    ax3.set_title(f'Top {top_n} Most Connected Sectors', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.invert_yaxis()

    # Plot 4: Correlation Matrix
    top_50_idx = np.argsort(correlation_strength)[::-1][:50]
    C_top = spectrum['correlation_matrix'][np.ix_(top_50_idx, top_50_idx)]

    im = ax4.imshow(C_top, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    ax4.set_title('Correlation Structure (Top 50)', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax4, label='Correlation')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_sensitivity_analysis(sensitivity_results, save_path):
    """Plot 8: Sensitivity analysis."""
    scenario_names = list(sensitivity_results.keys())
    total_changes = [sensitivity_results[s]['total_change'] for s in scenario_names]
    demand_contrib = [sensitivity_results[s]['demand_contribution'] for s in scenario_names]
    supply_contrib = [sensitivity_results[s]['supply_contribution'] for s in scenario_names]
    max_impacts = [abs(sensitivity_results[s]['max_impact_value']) for s in scenario_names]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    # Total impact
    colors = ['green' if x > 0 else 'red' for x in total_changes]
    ax1.bar(range(len(scenario_names)), total_changes, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_xticks(range(len(scenario_names)))
    ax1.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
    ax1.set_ylabel('Total Output Change', fontsize=10, fontweight='bold')
    ax1.set_title('Total Impact by Scenario', fontsize=11, fontweight='bold')
    ax1.axhline(y=0, color='black', linewidth=0.8)
    ax1.grid(True, alpha=0.3, axis='y')

    # Demand vs Supply
    x = np.arange(len(scenario_names))
    width = 0.35
    ax2.bar(x - width/2, demand_contrib, width, label='Demand', color='blue', alpha=0.7)
    ax2.bar(x + width/2, supply_contrib, width, label='Supply', color='red', alpha=0.7)
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel('Contribution', fontsize=10, fontweight='bold')
    ax2.set_title('Demand vs Supply Contribution', fontsize=11, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Max impact
    ax3.bar(range(len(scenario_names)), max_impacts, color='purple', alpha=0.7, edgecolor='black')
    ax3.set_xticks(range(len(scenario_names)))
    ax3.set_xticklabels(scenario_names, rotation=45, ha='right', fontsize=9)
    ax3.set_ylabel('Max Sectoral Impact (abs)', fontsize=10, fontweight='bold')
    ax3.set_title('Maximum Sectoral Impact', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    # Summary table
    ax4.axis('off')
    table_data = []
    for s in scenario_names:
        table_data.append([
            s,
            f"{sensitivity_results[s]['total_change']:.0f}",
            sensitivity_results[s]['max_impact_sector'][:20],
            f"{sensitivity_results[s]['max_impact_value']:.0f}"
        ])

    table = ax4.table(cellText=table_data,
                     colLabels=['Scenario', 'Total Δx', 'Max Sector', 'Max Value'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    ax4.set_title('Sensitivity Analysis Summary', fontsize=11, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_temporal_rmt_analysis(temporal_analyzer, save_path):
    """Plot 9: Temporal RMT evolution."""
    periods = temporal_analyzer.periods

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    market_modes = []
    turbulence_indices = []
    absorption_ratios = []
    outlier_fractions = []

    for period in periods:
        risk = temporal_analyzer.compute_systemic_risk_indicators(period)
        market_modes.append(risk['market_mode'])
        turbulence_indices.append(risk['turbulence_index'])
        absorption_ratios.append(risk['absorption_ratio'])
        outlier_fractions.append(risk['outlier_fraction'])

    # Market Mode
    axes[0, 0].plot(periods, market_modes, 'o-', linewidth=2, markersize=8, color='darkblue')
    axes[0, 0].fill_between(range(len(periods)), market_modes, alpha=0.3)
    axes[0, 0].set_ylabel('Market Mode', fontsize=10, fontweight='bold')
    axes[0, 0].set_title('Dominant Eigenvalue Evolution', fontsize=11, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # Turbulence
    colors_turb = ['green' if x < 0 else 'red' for x in turbulence_indices]
    axes[0, 1].bar(periods, turbulence_indices, color=colors_turb, alpha=0.7, edgecolor='black')
    axes[0, 1].set_ylabel('Turbulence Index', fontsize=10, fontweight='bold')
    axes[0, 1].set_title('Turbulence Level', fontsize=11, fontweight='bold')
    axes[0, 1].axhline(y=0, color='black', linewidth=0.8)
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # Absorption Ratio
    axes[1, 0].plot(periods, absorption_ratios, 's-', linewidth=2, markersize=8, color='purple')
    axes[1, 0].fill_between(range(len(periods)), absorption_ratios, alpha=0.3, color='purple')
    axes[1, 0].set_ylabel('Absorption Ratio', fontsize=10, fontweight='bold')
    axes[1, 0].set_title('Variance Concentration', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylim([0, 1])
    axes[1, 0].grid(True, alpha=0.3)

    # Outlier Fraction
    axes[1, 1].bar(periods, outlier_fractions, color='orange', alpha=0.7, edgecolor='black')
    axes[1, 1].set_ylabel('Fraction of Outliers', fontsize=10, fontweight='bold')
    axes[1, 1].set_title('Outlier Eigenvalue Fraction', fontsize=11, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    fig.suptitle('Temporal Evolution of Spectral Risk Indicators',
                fontsize=13, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_contagion_analysis(temporal_analyzer, crisis_period, normal_period, save_path):
    """Plot 10: Contagion analysis."""
    contagion = temporal_analyzer.detect_financial_contagion(crisis_period, normal_period)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Contagion metrics
    metrics_names = ['Market Mode\nChange (%)', 'Outlier Fraction\nChange (%)',
                     'Absorption Ratio\nChange (%)', 'Entropy\nChange (%)']
    metrics_values = [
        contagion['market_mode_change_pct'],
        contagion['outlier_fraction_change_pct'],
        contagion['absorption_ratio_change_pct'],
        -contagion['entropy_change_pct']
    ]
    colors_metrics = ['red' if x > 0 else 'green' for x in metrics_values]

    axes[0, 0].bar(metrics_names, metrics_values, color=colors_metrics, alpha=0.7, edgecolor='black')
    axes[0, 0].set_ylabel('Change (%)', fontsize=10, fontweight='bold')
    axes[0, 0].set_title('Contagion Indicators', fontsize=11, fontweight='bold')
    axes[0, 0].axhline(y=0, color='black', linewidth=0.8)
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # Contagion score gauge
    contagion_score = contagion['contagion_score']

    axes[0, 1].barh([0], [contagion_score], height=0.5, color='darkred', alpha=0.7)
    axes[0, 1].barh([0], [100-contagion_score], left=[contagion_score],
                   height=0.5, color='lightgray', alpha=0.3)
    axes[0, 1].set_xlim([0, 100])
    axes[0, 1].set_yticks([])
    axes[0, 1].set_xlabel('Contagion Score', fontsize=10, fontweight='bold')
    axes[0, 1].set_title(f'Assessment: {contagion["contagion_level"]}',
                        fontsize=11, fontweight='bold')
    axes[0, 1].text(contagion_score/2, 0, f'{contagion_score:.1f}',
                   ha='center', va='center', fontweight='bold', fontsize=12, color='white')

    # Crisis vs Normal
    crisis_risk = contagion['crisis_metrics']
    normal_risk = contagion['normal_metrics']

    metric_labels = ['Market Mode', 'Absorption Ratio', 'Turbulence']
    crisis_vals = [crisis_risk['market_mode'], crisis_risk['absorption_ratio'],
                  crisis_risk['turbulence_index']]
    normal_vals = [normal_risk['market_mode'], normal_risk['absorption_ratio'],
                  normal_risk['turbulence_index']]

    x_pos = np.arange(len(metric_labels))
    width = 0.35

    axes[1, 0].bar(x_pos - width/2, normal_vals, width, label=normal_period,
                  color='lightgreen', alpha=0.7, edgecolor='black')
    axes[1, 0].bar(x_pos + width/2, crisis_vals, width, label=crisis_period,
                  color='darkred', alpha=0.7, edgecolor='black')

    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(metric_labels, fontsize=9)
    axes[1, 0].set_ylabel('Value', fontsize=10, fontweight='bold')
    axes[1, 0].set_title('Risk Metric Comparison', fontsize=11, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Summary text
    axes[1, 1].axis('off')
    summary_text = (
        f"CONTAGION ANALYSIS\n"
        f"==================\n\n"
        f"Crisis: {crisis_period}\n"
        f"Normal: {normal_period}\n\n"
        f"Score: {contagion_score:.2f}\n"
        f"Level: {contagion['contagion_level']}\n\n"
        f"Changes:\n"
        f"• Market Mode: +{contagion['market_mode_change_pct']:.1f}%\n"
        f"• Outliers: +{contagion['outlier_fraction_change_pct']:.1f}%\n"
        f"• Absorption: +{contagion['absorption_ratio_change_pct']:.1f}%\n"
        f"• Entropy: {contagion['entropy_change_pct']:.1f}%"
    )

    axes[1, 1].text(0.1, 0.9, summary_text, transform=axes[1, 1].transAxes,
                   fontsize=10, verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    fig.suptitle(f'Financial Contagion: {crisis_period} vs {normal_period}',
                fontsize=14, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================================
# SECTION 7: DATA LOADING
# ============================================================================

def load_figaro_data(year: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load FIGARO data for a given year."""
    logger.info(f"Loading FIGARO {year} data...")

    sector_file = CONFIG['data_dir'] / f"sector_only_matrix_{year}.csv"
    demand_file = CONFIG['data_dir'] / f"final_demand_only_matrix_{year}.csv"
    va_file = CONFIG['data_dir'] / f"value_added_only_matrix_{year}.csv"

    for f in [sector_file, demand_file, va_file]:
        if not f.exists():
            raise FileNotFoundError(f"File not found: {f}")

    Z_df = pd.read_csv(sector_file, index_col=0)
    F_df = pd.read_csv(demand_file, index_col=0)
    V_df = pd.read_csv(va_file, index_col=0)

    return Z_df, F_df, V_df


def prepare_io_system(Z_df, F_df, V_df) -> Tuple[IOSystem, List[str]]:
    """Prepare IO system."""
    Z = Z_df.values.astype(float)
    F = F_df.values.astype(float)
    V = V_df.values.astype(float)

    sector_labels = Z_df.index.tolist()

    d = F.sum(axis=1)
    v = V.sum(axis=0)
    x = Z.sum(axis=1) + d
    x = np.maximum(x, TOLERANCE)

    io_system = IOSystem(Z, x, d, v)

    return io_system, sector_labels


# ============================================================================
# SECTION 8: MAIN ANALYSIS PIPELINE
# ============================================================================

def analyze_single_year(year: int):
    """Complete analysis for a single year."""
    logger.info(f"\n{'='*80}")
    logger.info(f"ANALYZING YEAR {year}")
    logger.info(f"{'='*80}\n")

    # Create year-specific directories
    year_results_dir = CONFIG['results_dir'] / str(year)
    year_figures_dir = CONFIG['figures_dir'] / str(year)
    year_results_dir.mkdir(exist_ok=True)
    year_figures_dir.mkdir(exist_ok=True)

    # Load data
    Z_df, F_df, V_df = load_figaro_data(year)
    io_system, sector_labels = prepare_io_system(Z_df, F_df, V_df)
    n_sectors = io_system.n

    logger.info(f"Loaded {n_sectors} sectors")
    logger.info(f"ρ(A) = {io_system.diagnostics['rho_A']:.6f}")
    logger.info(f"ρ(B) = {io_system.diagnostics['rho_B']:.6f}")

    # Spectral analysis
    A_eigenvalues = np.linalg.eigvals(io_system.A)
    B_eigenvalues = np.linalg.eigvals(io_system.B)

    A_props = {
        'eigenvalues': A_eigenvalues,
        'spectral_radius': np.max(np.abs(A_eigenvalues))
    }
    B_props = {
        'eigenvalues': B_eigenvalues,
        'spectral_radius': np.max(np.abs(B_eigenvalues))
    }

    # Shock generation
    shock_gen = ShockGenerator(n=n_sectors, seed=RANDOM_SEED + year)
    propagator = ShockPropagator(io_system)

    # Policy scenarios
    scenarios = generate_policy_shocks(shock_gen, n_sectors, sector_labels)
    logger.info(f"Generated {len(scenarios)} policy scenarios")

    # Run first scenario for detailed analysis
    first_scenario = list(scenarios.keys())[0]
    results = propagator.propagate_dual_shock(
        scenarios[first_scenario]['delta_f'],
        scenarios[first_scenario]['delta_v'],
        alpha=scenarios[first_scenario]['alpha'],
        beta=scenarios[first_scenario]['beta']
    )

    logger.info(f"Scenario: {scenarios[first_scenario]['name']}")
    logger.info(f"Total change: {results['total_change']:,.2f}")

    # Sensitivity analysis
    sensitivity_results = conduct_sensitivity_analysis(propagator, sector_labels, scenarios)

    # RMT shock matrix
    shock_matrix = shock_gen.generate_demand_shock_matrix(
        'random_correlated',
        {'n_shocks': min(200, n_sectors), 'mean': 0.0, 'std': 100.0, 'correlation': 0.5}
    )

    # VISUALIZATIONS
    logger.info("\nGenerating visualizations...")

    # Plot 1: Spectral comparison
    plot_spectral_comparison(
        A_props, B_props,
        year_figures_dir / 'plot_1_spectral_comparison.png'
    )
    logger.info("  ✓ plot_1_spectral_comparison.png")

    # Plot 2: Sector impact
    plot_sector_impact(
        sector_labels, results,
        year_figures_dir / 'plot_2_sector_impact.png',
        top_n=20
    )
    logger.info("  ✓ plot_2_sector_impact.png")

    # Plot 7: RMT analysis
    plot_rmt_analysis(
        shock_matrix, sector_labels,
        year_figures_dir / 'plot_7_rmt_analysis.png',
        top_n=50
    )
    logger.info("  ✓ plot_7_rmt_analysis.png")

    # Plot 8: Sensitivity analysis
    plot_sensitivity_analysis(
        sensitivity_results,
        year_figures_dir / 'plot_8_sensitivity_analysis.png'
    )
    logger.info("  ✓ plot_8_sensitivity_analysis.png")

    # CSV OUTPUTS
    logger.info("\nGenerating CSV files...")

    # figaro_shock_analysis_results.csv
    results_df = pd.DataFrame({
        'Sector': sector_labels,
        'Output': io_system.x,
        'Final_Demand': io_system.d,
        'Value_Added': io_system.v,
        'Demand_Impact': results['delta_x_demand'],
        'Supply_Impact': results['delta_x_supply'],
        'Total_Impact': results['delta_x_total'],
        'Impact_Percent': (results['delta_x_total'] / (io_system.x + 1e-10) * 100),
        'Backward_Linkages': np.sum(io_system.A, axis=0),
        'Forward_Linkages': np.sum(io_system.A, axis=1)
    })
    results_df = results_df.sort_values('Total_Impact', key=abs, ascending=False)
    results_df.to_csv(year_results_dir / 'figaro_shock_analysis_results.csv', index=False)
    logger.info("  ✓ figaro_shock_analysis_results.csv")

    # figaro_sensitivity_analysis.csv
    sensitivity_df = pd.DataFrame([
        {
            'Scenario': s,
            'Total_Change': sensitivity_results[s]['total_change'],
            'Demand_Contribution': sensitivity_results[s]['demand_contribution'],
            'Supply_Contribution': sensitivity_results[s]['supply_contribution'],
            'Max_Impact_Sector': sensitivity_results[s]['max_impact_sector'],
            'Max_Impact_Value': sensitivity_results[s]['max_impact_value']
        }
        for s in sensitivity_results
    ])
    sensitivity_df.to_csv(year_results_dir / 'figaro_sensitivity_analysis.csv', index=False)
    logger.info("  ✓ figaro_sensitivity_analysis.csv")

    # Save matrices
    np.save(year_results_dir / 'matrix_A_leontief.npy', io_system.A)
    np.save(year_results_dir / 'matrix_B_ghosh.npy', io_system.B)
    logger.info("  ✓ matrix_A_leontief.npy")
    logger.info("  ✓ matrix_B_ghosh.npy")

    logger.info(f"\n✓ Year {year} analysis complete")

    return {
        'year': year,
        'io_system': io_system,
        'sector_labels': sector_labels,
        'shock_matrix': shock_matrix,
        'results': results,
        'sensitivity_results': sensitivity_results
    }


def run_temporal_analysis(all_years_data):
    """Run temporal RMT and contagion analysis across all years."""
    logger.info(f"\n{'='*80}")
    logger.info("TEMPORAL RMT & CONTAGION ANALYSIS")
    logger.info(f"{'='*80}\n")

    # Collect shock matrices
    shock_matrices = {}
    for data in all_years_data:
        shock_matrices[str(data['year'])] = data['shock_matrix']

    # Use first year's labels
    sector_labels = all_years_data[0]['sector_labels']

    # Create temporal analyzer
    temporal_analyzer = TemporalRMTAnalyzer(
        shock_matrices,
        sector_labels,
        variance=CONFIG['rmt_variance']
    )

    # Kolmogorov-Smirnov tests
    logger.info("Performing KS tests...")
    ks_results = []
    for period in shock_matrices.keys():
        ks = temporal_analyzer.kolmogorov_smirnov_test(period)
        ks_results.append({
            'Period': period,
            'KS_Statistic': ks['ks_statistic'],
            'P_Value': ks['p_value'],
            'Significant': ks['significant'],
            'Interpretation': ks['interpretation'],
            'N_Eigenvalues_Tested': ks['n_eigenvalues_tested']
        })
        logger.info(f"  {period}: KS={ks['ks_statistic']:.4f}, p={ks['p_value']:.4f}")

    ks_df = pd.DataFrame(ks_results)
    ks_df.to_csv(CONFIG['results_dir'] / 'kolmogorov_smirnov_tests.csv', index=False)
    logger.info("  ✓ kolmogorov_smirnov_tests.csv")

    # Systemic risk indicators
    logger.info("\nComputing systemic risk indicators...")
    risk_results = []
    for period in shock_matrices.keys():
        risk = temporal_analyzer.compute_systemic_risk_indicators(period)
        risk_results.append({
            'Period': period,
            'Market_Mode': risk['market_mode'],
            'Turbulence_Index': risk['turbulence_index'],
            'Absorption_Ratio': risk['absorption_ratio'],
            'Shannon_Entropy': risk['shannon_entropy'],
            'Outlier_Fraction': risk['outlier_fraction']
        })

    risk_df = pd.DataFrame(risk_results)
    risk_df.to_csv(CONFIG['results_dir'] / 'temporal_systemic_risk_indicators.csv', index=False)
    logger.info("  ✓ temporal_systemic_risk_indicators.csv")

    # Plot 9: Temporal RMT evolution
    plot_temporal_rmt_analysis(
        temporal_analyzer,
        CONFIG['figures_dir'] / 'plot_9_temporal_rmt_analysis.png'
    )
    logger.info("  ✓ plot_9_temporal_rmt_analysis.png")

    # Contagion analysis (crisis=last year, normal=first year)
    periods = sorted(shock_matrices.keys())
    crisis_period = periods[-1]
    normal_period = periods[0]

    logger.info(f"\nContagion analysis: {crisis_period} vs {normal_period}")
    contagion = temporal_analyzer.detect_financial_contagion(crisis_period, normal_period)

    logger.info(f"  Contagion Score: {contagion['contagion_score']:.2f}")
    logger.info(f"  Level: {contagion['contagion_level']}")

    contagion_df = pd.DataFrame([{
        'Crisis_Period': crisis_period,
        'Normal_Period': normal_period,
        'Contagion_Score': contagion['contagion_score'],
        'Contagion_Level': contagion['contagion_level'],
        'Market_Mode_Change_Pct': contagion['market_mode_change_pct'],
        'Outlier_Fraction_Change_Pct': contagion['outlier_fraction_change_pct'],
        'Absorption_Ratio_Change_Pct': contagion['absorption_ratio_change_pct'],
        'Entropy_Change_Pct': contagion['entropy_change_pct']
    }])
    contagion_df.to_csv(CONFIG['results_dir'] / 'financial_contagion_analysis.csv', index=False)
    logger.info("  ✓ financial_contagion_analysis.csv")

    # Plot 10: Contagion analysis
    plot_contagion_analysis(
        temporal_analyzer, crisis_period, normal_period,
        CONFIG['figures_dir'] / 'plot_10_contagion_analysis.png'
    )
    logger.info("  ✓ plot_10_contagion_analysis.png")

    logger.info("\n✓ Temporal analysis complete")


def main():
    """Main execution function."""
    logger.info(f"\nStarting integrated analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Years to process: {CONFIG['years']}")

    all_years_data = []

    # Process each year
    for year in CONFIG['years']:
        try:
            year_data = analyze_single_year(year)
            all_years_data.append(year_data)
        except FileNotFoundError as e:
            logger.warning(f"Skipping year {year}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error processing year {year}: {e}")
            continue

    # Temporal analysis
    if len(all_years_data) >= 2:
        run_temporal_analysis(all_years_data)
    else:
        logger.warning("Insufficient data for temporal analysis (need >= 2 years)")

    logger.info(f"\n{'='*80}")
    logger.info("ANALYSIS COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"\nProcessed {len(all_years_data)} years successfully")
    logger.info(f"\nAll outputs saved to:")
    logger.info(f"  Results: {CONFIG['results_dir']}")
    logger.info(f"  Figures: {CONFIG['figures_dir']}")
    logger.info(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
