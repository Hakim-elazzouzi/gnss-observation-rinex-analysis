"""
gnss_utils.py
=============
Shared utility functions for the GNSS-Observation-RINEX project series.
All projects import from this module to avoid code duplication.

Author  : Hakim El Azzouzi
Degree  : MSc Global Navigation Satellite Systems
          Mohammed First University, Oujda, Morocco
Email   : elazzouzihakim10@gmail.com
LinkedIn: https://linkedin.com/in/Hakim-El-Azzouzi
Location: Luxembourg

Usage
-----
    import sys
    sys.path.append('../../shared/utils')
    from gnss_utils import load_obs, pick_snr_code, pick_pr_code, compute_L4, gnss_cmap

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import georinex as gr
import warnings

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# Physical constants
# ─────────────────────────────────────────────────────────────────
C = 299_792_458.0        # speed of light [m/s]

# GPS
F1_GPS  = 1_575.42e6
F2_GPS  = 1_227.60e6
F5_GPS  = 1_176.45e6
LAM1_GPS = C / F1_GPS   # ≈ 0.19029 m
LAM2_GPS = C / F2_GPS   # ≈ 0.24421 m
LAM5_GPS = C / F5_GPS

# Galileo (E1, E5a, E5b, E6)
F1_GAL  = 1_575.42e6
F5_GAL  = 1_176.45e6
F7_GAL  = 1_207.14e6
LAM1_GAL = C / F1_GAL
LAM5_GAL = C / F5_GAL

# GLONASS (nominal centre, channel 0)
F1_GLO  = 1_602.000e6
F2_GLO  = 1_246.000e6
LAM1_GLO = C / F1_GLO
LAM2_GLO = C / F2_GLO

# BeiDou (B1, B2)
F1_BDS  = 1_561.098e6
F2_BDS  = 1_207.140e6
LAM1_BDS = C / F1_BDS
LAM2_BDS = C / F2_BDS

# QZSS (same as GPS)
F1_QZS  = F1_GPS
F2_QZS  = F2_GPS
LAM1_QZS = LAM1_GPS
LAM2_QZS = LAM2_GPS

# Multipath coefficient for MP1
# MP1 = C1 - L1 - 2*(f2²/(f1²-f2²))*(L1-L2)
ALPHA_MP1_GPS = 2 * F2_GPS**2 / (F1_GPS**2 - F2_GPS**2)   # ≈ 1.5457

# L4 → STEC conversion [m/TECU] for GPS
ALPHA_IONO_GPS = 40.3e16 * (1/F1_GPS**2 - 1/F2_GPS**2)

# ─────────────────────────────────────────────────────────────────
# Constellation metadata
# ─────────────────────────────────────────────────────────────────
CONST_COLORS = {
    'G': '#2196F3',   # GPS     — blue
    'R': '#F44336',   # GLONASS — red
    'E': '#4CAF50',   # Galileo — green
    'C': '#FF9800',   # BeiDou  — orange
    'J': '#9C27B0',   # QZSS    — purple
    'S': '#00BCD4',   # SBAS    — cyan
}
CONST_NAMES = {
    'G': 'GPS', 'R': 'GLONASS', 'E': 'Galileo',
    'C': 'BeiDou', 'J': 'QZSS', 'S': 'SBAS',
}

# Best SNR codes to try per constellation (in priority order)
SNR_CODES = {
    'G': ['S1C', 'S2W'],
    'R': ['S1C', 'S1P'],
    'E': ['S1X', 'S5X'],
    'C': ['S1X', 'S2I'],
    'J': ['S1C', 'S1X'],
    'S': ['S1C'],
}

# Best pseudorange codes to try per constellation (in priority order)
PR_CODES = {
    'G': ['C1C', 'C2W'],
    'R': ['C1C', 'C1P'],
    'E': ['C1X', 'C5X'],
    'C': ['C1X', 'C2I'],
    'J': ['C1C', 'C1X'],
    'S': ['C1C'],
}

# Dual-frequency phase pairs for L4 computation
DUAL_FREQ = {
    'G': ('L1C', 'L2W',  LAM1_GPS, LAM2_GPS),
    'R': ('L1C', 'L2C',  LAM1_GLO, LAM2_GLO),
    'E': ('L1X', 'L5X',  LAM1_GAL, LAM5_GAL),
    'C': ('L1X', 'L2I',  LAM1_BDS, LAM2_BDS),
    'J': ('L1C', 'L2X',  LAM1_QZS, LAM2_QZS),
}

# ─────────────────────────────────────────────────────────────────
# File loading
# ─────────────────────────────────────────────────────────────────
def load_obs(obs_path, interval=30, verbose=True):
    """
    Load a RINEX 3 observation file and print its header.

    Parameters
    ----------
    obs_path : str   — path to the .rnx / .obs file
    interval : int   — sampling interval to keep [seconds]
    verbose  : bool  — print header and summary if True

    Returns
    -------
    obs      : xarray.Dataset — full observation dataset
    header   : dict           — parsed file header
    """
    header = gr.rinexheader(obs_path)

    if verbose:
        print("📋 FILE HEADER")
        print("=" * 60)
        for key, value in header.items():
            print(f"  {key:<25}: {value}")
        print()
        print("⏳ Loading observations...")

    obs = gr.load(obs_path, interval=interval)

    if verbose:
        print("✅ Data loaded!")
        print(f"   Satellites : {len(obs.sv)}")
        print(f"   Epochs     : {len(obs.time)}")
        print(f"   Variables  : {list(obs.data_vars)}")
        print()

    return obs, header


# ─────────────────────────────────────────────────────────────────
# Observable auto-detection
# ─────────────────────────────────────────────────────────────────
def pick_snr_code(obs, sat):
    """
    Return the first available SNR observable code for a satellite.

    Tries S1C, S1X, S1P, S2W in order.
    Returns (code, series) or (None, None) if nothing found.
    """
    prefix = sat[0]
    codes_to_try = SNR_CODES.get(prefix, ['S1C', 'S1X'])
    for code in codes_to_try:
        if code in obs.data_vars:
            s = obs[code].sel(sv=sat).to_series().dropna()
            if len(s) > 0:
                return code, s
    return None, None


def pick_pr_code(obs, sat):
    """
    Return the first available pseudorange observable code for a satellite.

    Tries C1C, C1X, C1P, C2I in order.
    Returns (code, series) or (None, None) if nothing found.
    """
    prefix = sat[0]
    codes_to_try = PR_CODES.get(prefix, ['C1C', 'C1X'])
    for code in codes_to_try:
        if code in obs.data_vars:
            s = obs[code].sel(sv=sat).to_series().dropna()
            if len(s) > 0:
                return code, s
    return None, None


def best_satellite(obs, prefix, min_epochs=20):
    """
    Return the satellite with the most valid pseudorange epochs
    for a given constellation prefix.

    Parameters
    ----------
    obs    : xarray.Dataset
    prefix : str  — constellation prefix e.g. 'G', 'E'
    min_epochs : int — minimum valid epochs required

    Returns
    -------
    sat    : str  — best satellite PRN
    pr     : pd.Series — pseudorange time series
    pr_code: str  — observable code used
    """
    sats = sorted([s for s in obs.sv.values if s.startswith(prefix)])
    best_sat, best_pr, best_code, best_n = None, None, None, 0
    for sat in sats:
        code, pr = pick_pr_code(obs, sat)
        if pr is not None and len(pr) > best_n:
            best_n, best_sat, best_pr, best_code = len(pr), sat, pr, code
    return best_sat, best_pr, best_code


# ─────────────────────────────────────────────────────────────────
# Geometry-Free (L4) combination
# ─────────────────────────────────────────────────────────────────
def compute_L4(obs, sat, l1_code, l2_code, lam1, lam2, min_epochs=10, detrend=True):
    """
    Compute the Geometry-Free carrier-phase combination for one satellite.

    L4 = Φ₁ − Φ₂  [metres]
       = (I₂ − I₁) + (λ₁N₁ − λ₂N₂) + noise

    All geometric terms cancel (range, clocks, troposphere).

    Parameters
    ----------
    obs       : xarray.Dataset
    sat       : str    — satellite PRN
    l1_code   : str    — L1 phase code e.g. 'L1C'
    l2_code   : str    — L2 phase code e.g. 'L2W'
    lam1, lam2: float  — wavelengths [m]
    min_epochs: int    — minimum common epochs required
    detrend   : bool   — if True, subtract first epoch (removes λN term)

    Returns
    -------
    pd.Series or None
    """
    if l1_code not in obs.data_vars or l2_code not in obs.data_vars:
        return None
    phi1 = obs[l1_code].sel(sv=sat).to_series().dropna() * lam1
    phi2 = obs[l2_code].sel(sv=sat).to_series().dropna() * lam2
    common = phi1.index.intersection(phi2.index)
    if len(common) < min_epochs:
        return None
    L4 = phi1[common] - phi2[common]
    if detrend:
        L4 = L4 - L4.iloc[0]
    return L4


# ─────────────────────────────────────────────────────────────────
# Multipath proxy MP1
# ─────────────────────────────────────────────────────────────────
def compute_MP1(obs, sat):
    """
    Compute the L1 multipath proxy MP1 for a GPS satellite.

    MP1 = C1C − Φ₁ − α · (Φ₁ − Φ₂)
        ≈ multipath on L1 code + noise
        (mean removed to eliminate ambiguity and ionosphere DC)

    Parameters
    ----------
    obs : xarray.Dataset
    sat : str — GPS satellite PRN (must start with 'G')

    Returns
    -------
    mp1 : pd.Series or None — MP1 [metres], mean-removed
    rms : float or None     — RMS of MP1 [metres]
    """
    needed = ['C1C', 'L1C', 'L2W']
    if not all(c in obs.data_vars for c in needed):
        return None, None
    try:
        code = obs['C1C'].sel(sv=sat).to_series().dropna()
        ph1  = obs['L1C'].sel(sv=sat).to_series().dropna() * LAM1_GPS
        ph2  = obs['L2W'].sel(sv=sat).to_series().dropna() * LAM2_GPS
        common = code.index.intersection(ph1.index).intersection(ph2.index)
        if len(common) < 10:
            return None, None
        mp1 = code[common] - ph1[common] - ALPHA_MP1_GPS * (ph1[common] - ph2[common])
        mp1 = mp1 - mp1.mean()   # remove DC (ambiguity + ionosphere)
        rms = float(np.sqrt(np.mean(mp1**2)))
        return mp1, rms
    except Exception:
        return None, None


# ─────────────────────────────────────────────────────────────────
# Colour maps
# ─────────────────────────────────────────────────────────────────
def gnss_cmap():
    """
    Standard GNSS SNR colourmap used across all projects.
    Dark (no signal) → purple → blue → cyan → green → yellow → orange.
    """
    return LinearSegmentedColormap.from_list(
        "gnss_snr",
        ["#0d1117", "#1a0533", "#2c3e8c", "#0099cc", "#00e676", "#ffeb3b", "#ff6f00"],
        N=256,
    )


def iono_cmap():
    """
    Diverging colourmap for ionospheric L4 heatmaps.
    Dark (no data) → blue (negative) → white (zero) → red (positive).
    """
    return LinearSegmentedColormap.from_list(
        "iono_div",
        ["#111111", "#0d47a1", "#42a5f5", "#e3f2fd", "#ef9a9a", "#b71c1c"],
        N=256,
    )


def gap_cmap():
    """
    Binary colourmap for data gap maps.
    Dark (gap/no data) → green (data present).
    """
    return LinearSegmentedColormap.from_list(
        "gap_map", ["#1a1a2e", "#00e676"], N=2
    )


# ─────────────────────────────────────────────────────────────────
# Heatmap rendering (imshow — fixes pcolormesh blank-plot bug)
# ─────────────────────────────────────────────────────────────────
def plot_heatmap(ax, matrix, time_index, row_labels, cmap,
                 vmin=15, vmax=55, sentinel=5, origin='upper'):
    """
    Render a satellite × time heatmap using imshow.

    Uses imshow instead of pcolormesh to avoid the well-known bug where
    pcolormesh silently drops the last column on 1-row matrices.

    Parameters
    ----------
    ax          : matplotlib Axes
    matrix      : np.ndarray  shape (n_sats, n_epochs) — may contain NaN
    time_index  : DatetimeIndex — time axis
    row_labels  : list of str  — satellite PRN labels (Y axis)
    cmap        : Colormap
    vmin, vmax  : float — colour scale limits
    sentinel    : float — value to replace NaN (should be < vmin)
    origin      : str   — 'upper' (row 0 at top) or 'lower'

    Returns
    -------
    im : AxesImage
    """
    import matplotlib.dates as mdates

    display = np.where(np.isnan(matrix), sentinel, matrix)
    n_rows  = matrix.shape[0]

    im = ax.imshow(
        display,
        aspect='auto',
        cmap=cmap,
        vmin=vmin, vmax=vmax,
        extent=[
            mdates.date2num(time_index[0]),
            mdates.date2num(time_index[-1]),
            -0.5, n_rows - 0.5,
        ],
        origin=origin,
    )
    ax.xaxis_date()
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=8)
    return im


# ─────────────────────────────────────────────────────────────────
# Plot styling helpers
# ─────────────────────────────────────────────────────────────────
def dark_style(ax):
    """Apply the standard dark GNSS theme to an Axes object."""
    ax.set_facecolor('#111827')
    ax.tick_params(colors='#aaaaaa')
    ax.grid(True, color='#222222', linewidth=0.5)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')


def dark_legend(ax, **kwargs):
    """Add a dark-themed legend to an Axes object."""
    legend = ax.legend(
        framealpha=0.3,
        facecolor='#1a1a2e',
        edgecolor='#444444',
        **kwargs,
    )
    for text in legend.get_texts():
        text.set_color('white')
    return legend
