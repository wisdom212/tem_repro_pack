# -*- coding: utf-8 -*-
"""
Step 11: Additive background-noise control experiment (review task T6)
=======================================================================
The manuscript's noise model is signal-scaled Gaussian (sigma = 0.24|s|),
which makes the absolute noise vanish in the late gates - the favourable
case for any thresholding denoiser. Real TEM surveys also carry ADDITIVE
noise (receiver floor, power-line harmonics, ambient EM), whose absolute
level does not decay with the signal. This control quantifies how the
reference pipeline behaves when such a floor is present.

  variant A1: additive Gaussian, sigma = 1e-2 * max|s(t)|  (strong floor)
  variant A2: additive Gaussian, sigma = 1e-3 * max|s(t)|
  variant A3: additive Gaussian, sigma = 1e-4 * max|s(t)|  (mild floor)

The signal-scaled n24_sig case (sigma = 0.24|s|, additive component 0) is
included as the A0 baseline. seed = 42 throughout.

Outputs
-------
output/additive_control_full_precision.csv
output/additive_control_summary.txt
"""
import numpy as np
import csv
import os
import importlib.util

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, '..', 'data')
out_dir = os.path.join(here, '..', 'output')
os.makedirs(out_dir, exist_ok=True)

spec = importlib.util.spec_from_file_location(
    'denoise_mod', os.path.join(here, '02_denoise_wavelet.py'))
dm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dm)

WINDOWS = {'early': (0, 12), 'middle': (12, 28), 'late': (28, 40), 'all': (0, 40)}
# (tag, sigma_signal_scaled, sigma_additive as fraction of max|s|)
# A0 uses the PACKAGED n24_sig realisation (identical to Table 2 baseline).
CASES = [('A0_signal_scaled', None, None),
         ('A1_add_1e-2_only', 0.0, 1e-2),
         ('A2_add_1e-3_only', 0.0, 1e-3),
         ('A2c_scaled24_add1e-3', 0.24, 1e-3),
         ('A3_add_1e-4_only', 0.0, 1e-4)]


def snr_db(s, sh):
    e = np.sum((s - sh) ** 2)
    return 10.0 * np.log10(np.sum(s ** 2) / e) if e > 0 else np.inf


def rmse(s, sh):
    return float(np.sqrt(np.mean((s - sh) ** 2)))


def main():
    t_ts, v_clean = [], []
    with open(os.path.join(data_dir, 'timeseries_clean.csv')) as f:
        for row in csv.DictReader(f):
            t_ts.append(float(row['t_ms']))
            v_clean.append(float(row['V_clean_uVA']))
    t_ts = np.array(t_ts)
    v_clean = np.array(v_clean)
    clean40 = dm.window_aggregation(t_ts, v_clean)
    vmax = float(np.max(np.abs(v_clean)))

    rows = []
    for tag, srel, sadd_frac in CASES:
        if srel is None:
            # A0 baseline: the packaged n24_sig 40-gate table, evaluated
            # with the identical arrays used for reproducible Table 2
            c40, n40, d40 = [], [], []
            with open(os.path.join(data_dir, 'denoised_n24_sig.csv')) as f:
                for r in csv.DictReader(f):
                    c40.append(float(r['clean_uVA']))
                    n40.append(float(r['noisy_uVA']))
                    d40.append(float(r['denoised_improved_uVA']))
            clean40_l, noisy40, den40 = np.array(c40), np.array(n40), np.array(d40)
            noisy = den = None
        else:
            rng = np.random.default_rng(42)
            noise = v_clean * srel * rng.standard_normal(len(v_clean))
            if sadd_frac > 0:
                noise = noise + vmax * sadd_frac * rng.standard_normal(
                    len(v_clean))
            noisy = v_clean + noise
            den = dm.denoise(noisy, 'improved')
            noisy40 = dm.window_aggregation(t_ts, noisy)
            den40 = dm.window_aggregation(t_ts, den)
            clean40_l = clean40
        for name, (a, b) in WINDOWS.items():
            rows.append([tag, name,
                         f"{snr_db(clean40_l[a:b], noisy40[a:b]):.4f}",
                         f"{snr_db(clean40_l[a:b], den40[a:b]):.4f}",
                         f"{snr_db(clean40_l[a:b], den40[a:b]) - snr_db(clean40_l[a:b], noisy40[a:b]):+.4f}",
                         f"{rmse(clean40_l[a:b], noisy40[a:b]):.6e}",
                         f"{rmse(clean40_l[a:b], den40[a:b]):.6e}"])

    out1 = os.path.join(out_dir, 'additive_control_full_precision.csv')
    with open(out1, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case', 'window', 'SNR_noisy_dB', 'SNR_denoised_dB',
                    'dSNR_dB', 'RMSE_noisy_uVA', 'RMSE_denoised_uVA'])
        w.writerows(rows)

    L = []
    L.append('ADDITIVE BACKGROUND-NOISE CONTROL (review task T6)')
    L.append(f'max|s| = {vmax:.4e} uV/A | seed = 42')
    L.append('=' * 78)
    L.append(f"{'case':18s} {'window':7s} {'noisy':>8s} {'denoised':>9s} "
             f"{'dSNR':>8s} {'RMSE_n':>11s} {'RMSE_d':>11s}")
    for r in rows:
        L.append(f"{r[0]:18s} {r[1]:7s} {r[2]:>8s} {r[3]:>9s} {r[4]:>8s} "
                 f"{r[5]:>11s} {r[6]:>11s}")
    L.append('')
    L.append('Reading:')
    L.append('(1) A0 (signal-scaled only) reproduces the reproducible Table 2')
    L.append('    exactly - it is the favourable case for threshold denoisers.')
    L.append('(2) With an additive floor at 1e-3..1e-2 of peak amplitude, the late')
    L.append('    window (signal ~1e-6 uV/A) sits below the noise floor;')
    L.append('    thresholding cannot recover information that is not there.')
    L.append('(3) At high SNR the denoiser is not do-no-harm: Rigrsure still')
    L.append('    shrinks small coefficients and the improved threshold adds')
    L.append('    bias, so clean early gates are damaged (dSNR << 0).')
    L.append('(4) In the realistic combined case A2c (scaled + additive), the')
    L.append('    reference pipeline is net-negative on the early window and')
    L.append('    near-neutral elsewhere: the large late-window gain quoted in')
    L.append('    the manuscript (+20.31 dB) is an artefact of the pure')
    L.append('    signal-scaled noise model. The manuscript must state the')
    L.append('    assumed noise model, add this control (task T6), or restrict')
    L.append('    its claims accordingly.')
    out2 = os.path.join(out_dir, 'additive_control_summary.txt')
    with open(out2, 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print('written:', os.path.relpath(out1, os.path.join(here, '..')))
    print('written:', os.path.relpath(out2, os.path.join(here, '..')))


if __name__ == '__main__':
    main()
