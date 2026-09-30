#!/usr/bin/env bash
# One-click reproduction of every number in this pack.
# Tested on Python 3.12.3, Ubuntu 24.04 (see requirements.txt).
set -euo pipefail
cd "$(dirname "$0")/src"
python3 01_make_synthetic_data.py
python3 02_denoise_wavelet.py n24_sig
python3 02_denoise_wavelet.py n5_sig
python3 02_denoise_wavelet.py n5_fs
python3 03_evaluate_metrics.py n24_sig
python3 03_evaluate_metrics.py n5_sig
python3 03_evaluate_metrics.py n5_fs
python3 04_audit_manuscript_table2.py
python3 05_make_figures.py
python3 06_build_figures_docx.py
python3 07_reproducible_table2.py
python3 08_figures_v2.py
python3 09_build_docx_v2.py
python3 10_mc_robustness.py
python3 11_additive_noise_control.py
python3 12_figures_v3.py
python3 13_build_docx_v3.py
echo "ALL DONE - see output/"
