# 🔧 Shared Utilities — gnss_utils.py

Common GNSS functions imported by all 8 projects to avoid code duplication.

## Usage

```python
import sys
sys.path.append('../../shared/utils')
from gnss_utils import load_obs, compute_L4, gnss_cmap, dark_style
```

## Available functions

| Function | Description |
|----------|-------------|
| `load_obs(path)` | Load RINEX file + print header |
| `pick_snr_code(obs, sat)` | Auto-detect best SNR code for a satellite |
| `pick_pr_code(obs, sat)` | Auto-detect best pseudorange code |
| `best_satellite(obs, prefix)` | Most-tracked satellite per constellation |
| `compute_L4(obs, sat, ...)` | Geometry-Free combination Φ₁−Φ₂ |
| `compute_MP1(obs, sat)` | L1 multipath proxy + RMS |
| `gnss_cmap()` | Standard SNR colourmap |
| `iono_cmap()` | Diverging ionospheric colourmap |
| `gap_cmap()` | Binary gap map colourmap |
| `plot_heatmap(ax, ...)` | imshow-based heatmap (fixes pcolormesh bug) |
| `dark_style(ax)` | Apply dark GNSS theme to Axes |
| `dark_legend(ax)` | Add dark-themed legend |

## Constants

`C`, `F1_GPS`, `F2_GPS`, `LAM1_GPS`, `LAM2_GPS`, `LAM1_GAL`, `LAM5_GAL`,
`LAM1_BDS`, `LAM2_BDS`, `LAM1_GLO`, `LAM2_GLO`, `ALPHA_MP1_GPS`,
`ALPHA_IONO_GPS`, `CONST_COLORS`, `CONST_NAMES`, `DUAL_FREQ`
