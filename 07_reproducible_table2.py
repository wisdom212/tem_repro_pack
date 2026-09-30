# -*- coding: utf-8 -*-
"""
Step 07: Reproducible Table 2 (full precision) + manuscript reconciliation
==========================================================================
This script addresses Review Task T1 (2026-09-30 R4 decision letter):
"Table 2 must be reproducible - rerun the pipeline at full precision and
provide a provenance statement."

It recomputes the three manuscript metrics (its Eqs. 9-11) on the four
windows of manuscript Table 2, at FULL PRECISION (no rounding), from the
reference pipeline output (data/denoised_n24_sig.csv, seed = 42), and
performs two automatic checks:

  [1] Identity closure: for each window,
          Delta_SNR  ==  20 * log10( RMSE_noisy / RMSE_denoised )
      because SNR = 10*log10(sum(s^2)/sum(e^2)) and
      RMSE = sqrt(mean(e^2)) are algebraic transforms of the same
      residual sum of squares. A single pipeline must satisfy this
      identity to within floating-point tolerance (~0.000 dB).

  [2] Manuscript reconciliation: the recomputed values are compared,
      cell by cell, with the numbers printed in the current manuscript
      (R3/R4 revision, Table 2). Printed values are hard-coded below
      exactly as they appear in the manuscript's Word XML (verified by
      independent two-file audit on 2026-09-30).

Outputs
-------
output/table2_reproducible_full_precision.csv
output/table2_reconciliation_vs_manuscript.csv
output/table2_identity_check.txt
"""
import numpy as np
import csv
import os

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, '..', 'data')
out_dir = os.path.join(here, '..', 'output')
os.makedirs(out_dir, exist_ok=True)
VARIANT = 'n24_sig'

WINDOWS = {
    'early':  (0, 12),   # gates 1-12,  0.080 - 0.650 ms
    'middle': (12, 28),  # gates 13-28, 0.820 - 8.450 ms
    'late':   (28, 40),  # gates 29-40, 10.70 - 45.20 ms
    'all':    (0, 40),   # gates 1-40,  0.080 - 45.20 ms
}

# Manuscript Table 2 as printed in the R3/R4 revision (from the
# manuscript's own Word XML, two-file audit, 2026-09-30).
MS_TABLE2 = {
    'early':  {'SNR_noisy': 17.92, 'SNR_den': 19.30, 'RMSE_noisy': 2.70e-2,
               'RMSE_den': 2.31e-2, 'MRE_noisy': 28.70, 'MRE_den': 13.30},
    'middle': {'SNR_noisy': 14.87, 'SNR_den': 24.82, 'RMSE_noisy': 3.32e-4,
               'RMSE_den': 1.04e-4, 'MRE_noisy': 40.50, 'MRE_den': 8.45},
    'late':   {'SNR_noisy': 11.67, 'SNR_den': 31.98, 'RMSE_noisy': 3.27e-7,
               'RMSE_den': 8.95e-8, 'MRE_noisy': 41.46, 'MRE_den': 15.49},
    'all':    {'SNR_noisy': 17.92, 'SNR_den': 19.30, 'RMSE_noisy': 1.48e-2,
               'RMSE_den': 1.26e-2, 'MRE_noisy': 41.46, 'MRE_den': 15.49},
}
# Note: late/all-window MRE printed values are taken from the metrics copy
# shipped with the revision; the XML audit verified SNR and RMSE cells.


def snr_db(s, sh):
    e = np.sum((s - sh) ** 2)
    return 10.0 * np.log10(np.sum(s ** 2) / e) if e > 0 else np.inf


def rmse(s, sh):
    return float(np.sqrt(np.mean((s - sh) ** 2)))


def mre_pct(s, sh):
    d = np.abs(s - sh) / np.maximum(np.abs(s), 1e-30)
    return float(np.max(d) * 100.0)


def load(variant):
    cols = {k: [] for k in ('clean_uVA', 'noisy_uVA', 'denoised_improved_uVA')}
    with open(os.path.join(data_dir, f'denoised_{variant}.csv')) as f:
        for row in csv.DictReader(f):
            for k in cols:
                cols[k].append(float(row[k]))
    return {k: np.array(v) for k, v in cols.items()}


def main():
    d = load(VARIANT)
    clean, noisy, den = d['clean_uVA'], d['noisy_uVA'], d['denoised_improved_uVA']

    # ---- full-precision recomputation ----
    fp = {}
    for name, (a, b) in WINDOWS.items():
        cs, ns, ds = clean[a:b], noisy[a:b], den[a:b]
        fp[name] = {
            'SNR_noisy': snr_db(cs, ns), 'SNR_den': snr_db(cs, ds),
            'RMSE_noisy': rmse(cs, ns),  'RMSE_den': rmse(cs, ds),
            'MRE_noisy': mre_pct(cs, ns), 'MRE_den': mre_pct(cs, ds),
        }
        fp[name]['dSNR'] = fp[name]['SNR_den'] - fp[name]['SNR_noisy']
        fp[name]['dRMSE_dB'] = 20.0 * np.log10(fp[name]['RMSE_noisy']
                                               / fp[name]['RMSE_den'])
        fp[name]['identity_gap_dB'] = fp[name]['dSNR'] - fp[name]['dRMSE_dB']

    # ---- [1] write reproducible Table 2 (full precision) ----
    out1 = os.path.join(out_dir, 'table2_reproducible_full_precision.csv')
    with open(out1, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['window', 'gates', 'state', 'SNR_dB', 'RMSE_uVA', 'MRE_pct'])
        gate_lab = {'early': '1-12', 'middle': '13-28', 'late': '29-40',
                    'all': '1-40'}
        for name in WINDOWS:
            for st in ('noisy', 'den'):
                w.writerow([name, gate_lab[name],
                            'noisy' if st == 'noisy' else 'denoised_improved',
                            f"{fp[name]['SNR_' + st]:.4f}",
                            f"{fp[name]['RMSE_' + st]:.6e}",
                            f"{fp[name]['MRE_' + st]:.4f}"])
            w.writerow([name, gate_lab[name], 'gain_SNR_dB',
                        f"{fp[name]['dSNR']:.4f}", '', ''])
            w.writerow([name, gate_lab[name], 'gain_RMSE_ratio_dB',
                        f"{fp[name]['dRMSE_dB']:.4f}", '', ''])
            w.writerow([name, gate_lab[name], 'identity_gap_dB',
                        f"{fp[name]['identity_gap_dB']:.6f}", '',
                        'PASS' if abs(fp[name]['identity_gap_dB']) < 0.01
                        else 'FAIL'])

    # ---- [2] reconciliation vs manuscript printed values ----
    out2 = os.path.join(out_dir, 'table2_reconciliation_vs_manuscript.csv')
    verdict_rows = []
    with open(out2, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['window', 'cell', 'manuscript_printed',
                    'reference_pipeline_full_precision',
                    'abs_delta', 'consistent_at_printed_precision'])
        checks = [('SNR_noisy', 2), ('SNR_den', 2),
                  ('RMSE_noisy', None), ('RMSE_den', None),
                  ('MRE_noisy', 2), ('MRE_den', 2)]
        for name in WINDOWS:
            for cell, nd in checks:
                ms = MS_TABLE2[name][cell]
                rp = fp[name][cell]
                if nd is not None:
                    ok = abs(round(rp, nd) - ms) < 10 ** (-nd)
                else:
                    # RMSE: manuscript prints 2-3 sig figs; accept if the
                    # printed value is within 1% of the recomputed one
                    ok = abs(rp - ms) / ms <= 0.01
                w.writerow([name, cell, ms, f'{rp:.6e}' if nd is None
                            else f'{rp:.4f}',
                            f'{abs(rp - ms):.6e}' if nd is None
                            else f'{abs(rp - ms):.4f}',
                            'YES' if ok else 'NO'])
                verdict_rows.append((name, cell, ok))

    # ---- human-readable report ----
    out3 = os.path.join(out_dir, 'table2_identity_check.txt')
    L = []
    L.append('REPRODUCIBLE TABLE 2 - full-precision reference pipeline output')
    L.append(f'variant: {VARIANT} | seed: 42 | data: data/denoised_{VARIANT}.csv')
    L.append('=' * 72)
    hdr = ('window   SNR_n(dB)    SNR_d(dB)    dSNR     RMSE_n        '
           'RMSE_d        dSNR_id  gap')
    L.append(hdr)
    for name in WINDOWS:
        v = fp[name]
        L.append(f"{name:8s} {v['SNR_noisy']:10.4f} {v['SNR_den']:10.4f} "
                 f"{v['dSNR']:7.3f}  {v['RMSE_noisy']:11.4e} "
                 f"{v['RMSE_den']:11.4e}  {v['dRMSE_dB']:7.3f}  "
                 f"{v['identity_gap_dB']:+.6f}")
    L.append('')
    L.append('[1] IDENTITY CHECK (dSNR must equal 20*log10(RMSE_n/RMSE_d))')
    for name in WINDOWS:
        g = fp[name]['identity_gap_dB']
        L.append(f"  {name:8s} gap = {g:+.6f} dB  ->  "
                 f"{'PASS' if abs(g) < 0.01 else 'FAIL'}")
    L.append('')
    L.append('[2] RECONCILIATION vs manuscript printed Table 2 (R3/R4)')
    bad = [(n, c) for n, c, ok in verdict_rows if not ok]
    for n, c, ok in verdict_rows:
        L.append(f"  {n:8s} {c:10s} {'consistent' if ok else 'DIFFERS'}")
    L.append('')
    L.append(f'SUMMARY: identity closure {"PASSes" if all(abs(fp[n]["identity_gap_dB"]) < 0.01 for n in WINDOWS) else "FAILs"} on all 4 windows; '
             f'{len(verdict_rows) - len(bad)}/{len(verdict_rows)} manuscript cells consistent.')
    if bad:
        L.append('Cells that DIFFER from the manuscript print:')
        for n, c in bad:
            L.append(f'  - {n} / {c}: manuscript {MS_TABLE2[n][c]} vs '
                     f'pipeline {fp[n][c]:.6e}')
        L.append('')
        L.append('Interpretation: SNR and RMSE are algebraic transforms of the')
        L.append('same residual sum of squares; no single pipeline can reproduce')
        L.append('the manuscript SNR column while producing different middle/late')
        L.append('RMSE values. Either the manuscript RMSE cells came from a')
        L.append('different (undisclosed) computation, or they are transcription')
        L.append('errors. Per Task T1 the two sets cannot both stand: reprint')
        L.append('Table 2 from a single rerun pipeline and state its provenance.')
    with open(out3, 'w') as f:
        f.write('\n'.join(L) + '\n')

    print('\n'.join(L))
    print('written:', os.path.relpath(out1, os.path.join(here, '..')))
    print('written:', os.path.relpath(out2, os.path.join(here, '..')))
    print('written:', os.path.relpath(out3, os.path.join(here, '..')))


if __name__ == '__main__':
    main()
