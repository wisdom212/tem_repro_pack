# -*- coding: utf-8 -*-
"""
Step 10: Monte-Carlo robustness, 60 realisations (manuscript Table 3 provenance)
================================================================================
The manuscript revision (R3/R4) reports, in its Table 3 discussion, a Monte
Carlo expectation for the all-window SNR gain of the reference pipeline:
E[Delta_SNR] = +0.36 dB, std = 2.89 dB, P(Delta_SNR > 3 dB) = 0.15.
This script reproduces that statistic end-to-end:

  for i = 1..60:
      seed_i = 1000 + i
      noisy_i(t) = clean(t) * (1 + 0.24 * randn)   [signal-scaled, as disclosed]
      denoised_i = reference pipeline (sym8 / 5-level / Rigrsure / improved)
      Delta_SNR_i = SNR_all(denoised_i) - SNR_all(noisy_i)

Outputs
-------
output/table3_mc60_full_precision.csv   per-seed, per-window Delta_SNR
output/table3_mc60_summary.txt          distribution summary
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

N_RUNS = 60
SIGMA_REL = 0.24  # signal-scaled noise, disclosed level (n24_sig)
WINDOWS = {'early': (0, 12), 'middle': (12, 28), 'late': (28, 40), 'all': (0, 40)}


def snr_db(s, sh):
    e = np.sum((s - sh) ** 2)
    return 10.0 * np.log10(np.sum(s ** 2) / e) if e > 0 else np.inf


def main():
    t_ts, v_clean = [], []
    with open(os.path.join(data_dir, 'timeseries_clean.csv')) as f:
        for row in csv.DictReader(f):
            t_ts.append(float(row['t_ms']))
            v_clean.append(float(row['V_clean_uVA']))
    t_ts = np.array(t_ts)
    v_clean = np.array(v_clean)

    clean40 = dm.window_aggregation(t_ts, v_clean)
    rows, d_all = [], []
    for i in range(1, N_RUNS + 1):
        rng = np.random.default_rng(1000 + i)
        noisy = v_clean * (1.0 + SIGMA_REL * rng.standard_normal(len(v_clean)))
        den = dm.denoise(noisy, 'improved')
        den40 = dm.window_aggregation(t_ts, den)
        noisy40 = dm.window_aggregation(t_ts, noisy)
        rec = {'seed': 1000 + i}
        for name, (a, b) in WINDOWS.items():
            d = snr_db(clean40[a:b], den40[a:b]) - snr_db(clean40[a:b], noisy40[a:b])
            rec[name] = d
            if name == 'all':
                d_all.append(d)
        rows.append(rec)

    out1 = os.path.join(out_dir, 'table3_mc60_full_precision.csv')
    with open(out1, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['seed', 'dSNR_early_dB', 'dSNR_middle_dB',
                    'dSNR_late_dB', 'dSNR_all_dB'])
        for r in rows:
            w.writerow([r['seed'], f"{r['early']:.4f}", f"{r['middle']:.4f}",
                        f"{r['late']:.4f}", f"{r['all']:.4f}"])

    a = np.array(d_all)
    L = []
    L.append('MONTE CARLO ROBUSTNESS - reference pipeline, 60 realisations')
    L.append(f'noise model: signal-scaled Gaussian, sigma = {SIGMA_REL}|s(t)|')
    L.append(f'seeds: 1001..{1000 + N_RUNS} | wavelet sym8/5-level/Rigrsure/improved')
    L.append('=' * 64)
    L.append(f'all-window Delta_SNR: mean = {a.mean():+.4f} dB, '
             f'std = {a.std(ddof=1):.4f} dB')
    L.append(f'median = {np.median(a):+.4f} dB | min = {a.min():+.4f} | '
             f'max = {a.max():+.4f}')
    L.append(f'P(Delta_SNR > 3 dB) = {(a > 3).mean():.4f}  '
             f'({int((a > 3).sum())}/{N_RUNS})')
    L.append(f'P(Delta_SNR < 0)    = {(a < 0).mean():.4f}  '
             f'({int((a < 0).sum())}/{N_RUNS})')
    for name in ('early', 'middle', 'late'):
        v = np.array([r[name] for r in rows])
        L.append(f'{name:7s}: mean = {v.mean():+.4f} +/- {v.std(ddof=1):.4f} dB, '
                 f'P(>3dB) = {(v > 3).mean():.3f}, P(<0) = {(v < 0).mean():.3f}')
    L.append('')
    L.append('Interpretation: the single-implementation gain quoted in a')
    L.append('manuscript (+1.38 dB all-window at seed 42, +20.31 dB late window)')
    L.append('is one draw from this distribution. Report E and dispersion, not')
    L.append('single draws (review task T5).')
    out2 = os.path.join(out_dir, 'table3_mc60_summary.txt')
    with open(out2, 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L))
    print('written:', os.path.relpath(out1, os.path.join(here, '..')))
    print('written:', os.path.relpath(out2, os.path.join(here, '..')))


if __name__ == '__main__':
    main()
