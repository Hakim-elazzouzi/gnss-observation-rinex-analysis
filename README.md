# 🛰️ GNSS Observation RINEX Analysis

> **A series of 8 independent Python projects analysing raw GNSS observations  
> from a RINEX 3.05 file — from single-satellite pseudorange to multipath characterisation.**

---

**Author:** Hakim El Azzouzi  
**Degree:** MSc Global Navigation Satellite Systems — Mohammed First University, Oujda, Morocco  
**Email:** elazzouzihakim10@gmail.com  
**LinkedIn:** [linkedin.com/in/Hakim-El-Azzouzi](https://www.linkedin.com/in/elazzouzihakim/)  
**Location:** Luxembourg 🇱🇺

---

## 📖 About This Repository

Modern GNSS receivers produce **RINEX observation files** — standardised text files
containing raw measurements from every satellite the receiver can see. This repository
works through one such file step by step, building from the most basic analysis
(a single satellite's pseudorange arc) to a full site quality report and multipath
characterisation.

Every project is **fully independent**: run any notebook in isolation.  
All notebooks share a single RINEX file stored in `data/` and common utility
functions in `shared/utils/gnss_utils.py`.

---

## 📡 The RINEX File

```
data/AUCK00NZL_R_20260010000_01D_30S_MO.rnx
```

| Field | Value |
|-------|-------|
| Station | AUCK00NZL — Auckland, New Zealand |
| Receiver | TRIMBLE ALLOY |
| Antenna | TRM115000.00 |
| Network | CDDIS / LINZ CDDIS NASA |
| Date | 2026-01-01 (Day of Year 001) |
| Duration | 24 hours |
| Sampling | 30 seconds |
| Format | RINEX 3.05 |
| Constellations | GPS · GLONASS · Galileo · BeiDou · QZSS |

---

## 🗂️ Repository Structure

```
GNSS-Observation-RINEX/
│
├── data/
│   └── AUCK00NZL_R_20260010000_01D_30S_MO.rnx   ← shared observation file
│
├── projects/
│   ├── project_1/   gnss-single-satellite-analysis — Pseudorange & SNR Heatmap
│   ├── project_2/   gnss-gps-constellation-analysis — Fleet Pseudorange & SNR Heatmap
│   ├── project_3/   gnss-multi-constellation-analysis — One Satellite per System
│   ├── project_4/   gnss-pseudorange-carrier-phase-analysis — Comparaison
│   ├── project_5/   gnss-constellation-summary-analysis — Pie Chart & Histograms
│   ├── project_6/   gnss-ionospheric-delay-analysis — Geometry-Free Combination
│   ├── project_7/   gnss-multipath-analysis — MP1 · MP2 · Sidereal Repeat
│   └── project_8/   gnss-data-quality-assessment
├── shared/
│   └── utils/
│       ├── gnss_utils.py    ← shared functions (load, compute L4, MP1, colormaps…)
│       ├── __init__.py
│       └── README.md
├── **README.md**    ← you are here
└── LICENSE
```

---

## 📊 Project Overview

| # | Project | Key Observables | Plots |
|---|---------|----------------|-------|
| **1** | [gnss-single-satellite-analysis](projects/single_satellite_analysis @ f929ee7/) | C1C, S1C | Pseudorange arc · SNR heatmap |
| **2** | [gnss-gps-constellation-analysis](projects/all_gps_constellation_analysis @ 888c0bf/) | C1C, S1C | All arcs overlaid · Fleet heatmap · Availability |
| **3** | [gnss-multi-constellation-analysis](projects/multi_constellation_gnss_analysis @ 2a095c9/) | C1C/C1X, S1C/S1X | 5-system comparison · Stacked availability |
| **4** | [gnss-pseudorange-carrier-phase-analysis](projects/pseudorange_vs_phase_analysis @ 52524b8/) | C1C, L1C, L2W | Noise comparison · P−Φ · Detrended ionosphere |
| **5** | [gnss-constellation-summary-analysis](projects/projects/gnss_constellation_summary_analysis @ 64ee307/) | All | Pie chart · Histograms · Box plots · Full heatmap |
| **6** | [gnss-ionospheric-delay-analysis](projects/gnss_ionospheric_delay_analysis @ 894bdb1/) | L1C, L2W, L1X, L5X | L4 time series · Heatmap · ROTI |
| **7** | [gnss-multipath-analysis](projects/gnss_multipath_analysis @ 1575c94/) | C1C, L1C, L2W, C2W | MP1/MP2 time series · Heatmap · RMS ranking · Sidereal |
| **8** | [gnss-data-quality-assessment](projects/gnss_data_quality_report @ 82a26b4/) | All | Dashboard · Gap map · Scatter · Text report |

---

## ⚙️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/gnss-observation-rinex-analysis.git
cd gnss-observation-rinex-analysis
```

### 2. Install dependencies
All projects share the same requirements:
```bash
pip install -r projects/project_1/requirements.txt
```

Or install manually:
```bash
pip install georinex xarray pandas numpy matplotlib
```

### 3. Add the RINEX file
Place your RINEX 3 observation file in the `data/` folder.  
Each notebook has a clearly marked cell:
```python
obs_path = "../../data/YOUR_FILE.rnx"   # ← update this
```

### 4. Run any project
```bash
cd projects/single_satellite_analysis @ f929ee7/src
jupyter notebook project1_single_gps_satellite.py
```

---

## 🔧 Shared Utilities

All projects can import from `shared/utils/gnss_utils.py`:

```python
import sys
sys.path.append('../../shared/utils')
from gnss_utils import (
    load_obs,          # load RINEX file + print header
    pick_snr_code,     # auto-detect best SNR observable for a satellite
    pick_pr_code,      # auto-detect best pseudorange observable
    best_satellite,    # pick best-tracked satellite per constellation
    compute_L4,        # geometry-free carrier-phase combination
    compute_MP1,       # L1 multipath proxy
    gnss_cmap,         # standard GNSS SNR colourmap
    iono_cmap,         # diverging ionospheric colourmap
    plot_heatmap,      # imshow-based heatmap (fixes pcolormesh bug)
    dark_style,        # apply dark theme to any Axes
    CONST_COLORS,      # constellation colour palette
    CONST_NAMES,       # constellation name dictionary
)
```

---

## 📐 GNSS Observables Reference

| Code | Description | Unit |
|------|-------------|------|
| `C1C` | Pseudorange L1 C/A (GPS) | metres |
| `C1X` | Pseudorange L1 combined (Galileo/BeiDou) | metres |
| `L1C` | Carrier phase L1 C/A | cycles |
| `L2W` | Carrier phase L2 P(Y) (GPS) | cycles |
| `S1C` | SNR on L1 C/A | dB-Hz |
| `S1X` | SNR on L1 combined | dB-Hz |

### Satellite prefixes
| Prefix | System |
|--------|--------|
| `G` | GPS (USA) |
| `R` | GLONASS (Russia) |
| `E` | Galileo (Europe) |
| `C` | BeiDou (China) |
| `J` | QZSS (Japan) |

---

## 🔬 Key GNSS Equations

```
Pseudorange:     P = ρ + c(dT−dt) + I + T + εP
Carrier phase:   Φ = ρ + c(dT−dt) − I + T + λN + εΦ
Code−Phase:      P−Φ = 2I + λN + noise
Geometry-Free:   L4 = Φ1 − Φ2 = (I2−I1) + (λ1N1−λ2N2)
Multipath MP1:   MP1 = C1C − Φ1 − α(Φ1−Φ2),   α = 2f2²/(f1²−f2²)
Sidereal shift:  Δt = 24h − 23h56m4.1s ≈ 3m56s per solar day
```

---

## 🌐 Next Repository

**Coming next:** `GNSS-Navigation-RINEX` — a companion series analysing  
GNSS navigation (broadcast ephemeris) files: satellite positions, clock corrections,  
orbit visualisation, and positioning with navigation data.

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## ⭐ If this helped you

If you found this project useful for your own GNSS work or studies,  
please consider leaving a ⭐ on GitHub — it helps others find the series!
