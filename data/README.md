# data/

This folder contains the shared RINEX 3 observation file used by all 8 projects.

## File

```
AUCK00NZL_R_20260010000_01D_30S_MO.rnx
```

| Field | Value |
|-------|-------|
| Station | AUCK00NZL — Auckland, New Zealand |
| Network | GeoNet / LINZ Geodetic Network |
| Date | 2026-01-01 |
| Duration | 24 hours |
| Sampling | 30 seconds |
| Format | RINEX 3.05 |

## Why is the file not in this repository?

RINEX files are large (typically 50–300 MB for a 24-hour, 30-second file).
GitHub has a 100 MB file size limit and recommends against committing large binary files.

## How to get it

Download directly from [LINZ / CDDIS](https://cddis.nasa.gov/archive/gnss/data/daily/2026/001/26o/AUCK00NZL_R_20260010000_01D_30S_MO.rnx.gz):

1. Go to the CDDIS Nasa website
2. Create an account
2. Then navigate to archive/gnss/data/daily
3. Select date `2026-001`
4. Download the 30-second RINEX 3 observation file
5. Place it here as `AUCK00NZL_R_20260010000_01D_30S_MO.rnx`

## Using your own file

Any RINEX 3 observation file works. Place it here and update `obs_path` in each notebook:

```python
obs_path = "../../data/YOUR_FILE.rnx"
```
