# tempest-helper

Tool for automatic screen parameter discovery from HDMI electromagnetic emissions, used in TEMPEST-style attacks.

---

## Overview

TEMPEST attacks exploit electromagnetic emissions to recover screen contents. This tool automates the detection of key screen parameters—primarily the pixel clock—by analyzing emissions from an HDMI cable using a software-defined radio (SDR).

---

## Features

- Pixel clock estimation from RF emissions
- Harmonic-based noise filtering
- Frame-level correlation for candidate validation
- Modular Python code using GNU Radio

---

## Requirements

- Python 3.11+
- GNU Radio 3.10+
- SDR drivers (`osmosdr`, `uhd`)
- `numpy`
- `PyQt5`
- `js2py`

Install with:

```
pip install numpy PyQt5 js2py
```

---

## Usage

```
python main.py [options]
```

### Options

- `-h`, `--help`  
  Show help message and exit

- `-v`, `--verbose`  
  Enable verbose output

- `--folder FOLDER`  
  Path to save or read signal traces (default: `traces/`)

- `--skip-record`  
  Skip steps 1 and 2 and reuse existing traces in `--folder`

- `--sdr SDR`  
  Choose SDR backend: `hackrf` (default) or `usrp`

- `--step [1-4]`  
  Run until specified step (default: 3):  
  - 1 = Energy detection  
  - 2 = Trace recording  
  - 3 = Frame correlation  
  - 4 = Autocorrelation

- `--custom-list CUSTOM_LIST`  
  Path to a custom list of display modes (default: `modes.txt`)

---

## How It Works

1. **Energy Detection:** Measure RF signal strength at harmonic frequencies (>500 MHz).
2. **Trace Recording:** Save short RF captures for high-energy candidates.
3. **Correlation:** Compute Pearson correlation between frames to filter out noise.
4. **Output:** Return best matching display modes and rasterization parameters (pixel clock, Htot, Vtot, FPS).

---

## Notes

- Uses `videotimings.py` (from transpiled JS) to compute full timing parameters for display standards (CVT, DMT, CEA, etc.).
- File naming convention: `HxV@fps#standard.trace`
- Correlation is based on frame timing derived from sample rate and estimated refresh rate.
- Tool assumes screen content is mostly static (text, static UIs).

---

## Output Example

After running step 3:

```
[OK] 1920x1080@60#cvt -> 173.00 MHz | 2576x1120 @ 60Hz | corr=0.69
[OK] 1280x720@60#cea  -> 74.25 MHz  | 1650x750  @ 60Hz | corr=0.45
```

---

## Limitations & Future Work

- Integration with raster tools like TempestSDR is still manual.
- Improving signal acquisition range with LNA and directional antennas.
- Possible line-by-line correlation for better precision.

---

## References

- van Eck, W. (1985) – Electromagnetic radiation from video display units
- TempestSDR: https://github.com/martinmarinov/TempestSDR
- gr-tempest: https://ieeexplore.ieee.org/document/9946053
- Video Timings Calculator: https://tomverbeure.github.io/video_timings_calculator

---

**Note:** For research and educational use only.
