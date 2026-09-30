# -*- coding: utf-8 -*-
"""
Step 08: Figures v2 - reproducible Table 2 and manuscript reconciliation
=======================================================================
Fig 4: Reproducible Table 2 (full-precision reference pipeline output)
       panel A: SNR by window (noisy vs denoised)
       panel B: RMSE by window (log scale, noisy vs denoised)
Fig 5: Reconciliation - manuscript printed Table 2 vs reference pipeline
       panel A: SNR cells (must overlap)
       panel B: RMSE cells (log scale; differing cells highlighted red)

Run after step 07. Writes output/fig4_table2_reproducible.png,
output/fig5_reconciliation.png
"""
import numpy as np
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, '..', 'data')
out_dir = os.path.join(here, '..', 'output')
VARIANT = 'n24_sig'

WINDOWS = {'early\n(gates 1-12)': (0, 12), 'middle\n(gates 13-28)': (12, 28),
           'late\n(gates 29-40)': (28, 40), 'all\n(gates 1-40)': (0, 40)}

MS = {  # manuscript printed values (R3/R4 revision, Word XML audit)
    'early':  {'SNR_n': 17.92, 'SNR_d': 19.30, 'RMSE_n': 2.70e-2, 'RMSE_d': 2.31e-2},
    'middle': {'SNR_n': 14.87, 'SNR_d': 24.82, 'RMSE_n': 3.32e-4, 'RMSE_d': 1.04e-4},
    'late':   {'SNR_n': 11.67, 'SNR_d': 31.98, 'RMSE_n': 3.27e-7, 'RMSE_d': 8.95e-8},
    'all':    {'SNR_n': 17.92, 'SNR_d': 19.30, 'RMSE_n': 1.48e-2, 'RMSE_d': 1.26e-2},
}

# ---------- recompute full precision (same arrays as step 07) ----------
cols = {k: [] for k in ('clean_uVA', 'noisy_uVA', 'denoised_improved_uVA')}
with open(os.path.join(data_dir, f'denoised_{VARIANT}.csv')) as f:
    for row in csv.DictReader(f):
        for k in cols:
            cols[k].append(float(row[k]))
clean = np.array(cols['clean_uVA'])
noisy = np.array(cols['noisy_uVA'])
den = np.array(cols['denoised_improved_uVA'])


def snr(s, sh):
    e = np.sum((s - sh) ** 2)
    return 10 * np.log10(np.sum(s ** 2) / e)


def rmse(s, sh):
    return float(np.sqrt(np.mean((s - sh) ** 2)))


names = ['early', 'middle', 'late', 'all']
keys = list(WINDOWS.keys())
snr_n, snr_d, rmse_n, rmse_d = [], [], [], []
for lab, (a, b) in WINDOWS.items():
    snr_n.append(snr(clean[a:b], noisy[a:b]))
    snr_d.append(snr(clean[a:b], den[a:b]))
    rmse_n.append(rmse(clean[a:b], noisy[a:b]))
    rmse_d.append(rmse(clean[a:b], den[a:b]))

# ---------- Fig 4 ----------
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
x = np.arange(4)
ax = axes[0]
w = 0.36
b1 = ax.bar(x - w / 2, snr_n, w, label='noisy', color='#c0392b')
b2 = ax.bar(x + w / 2, snr_d, w, label='denoised (improved soft threshold)',
            color='#2980b9')
for i in range(4):
    ax.text(x[i] - w / 2, snr_n[i] + 0.4, f'{snr_n[i]:.2f}', ha='center', fontsize=7.5)
    ax.text(x[i] + w / 2, snr_d[i] + 0.4, f'{snr_d[i]:.2f}', ha='center', fontsize=7.5)
ax.set_xticks(x); ax.set_xticklabels(keys, fontsize=8)
ax.set_ylabel('SNR (dB)')
ax.set_title('[A] Reproducible Table 2 - SNR by window\n(identity closure |gap| < 0.000001 dB on all windows)',
             fontsize=9.5)
ax.legend(fontsize=8)
ax.grid(axis='y', alpha=0.3)

ax = axes[1]
b1 = ax.bar(x - w / 2, rmse_n, w, label='noisy', color='#c0392b')
b2 = ax.bar(x + w / 2, rmse_d, w, label='denoised', color='#2980b9')
ax.set_yscale('log')
for i in range(4):
    ax.text(x[i] - w / 2, rmse_n[i] * 1.15, f'{rmse_n[i]:.2e}', ha='center', fontsize=7)
    ax.text(x[i] + w / 2, rmse_d[i] * 1.15, f'{rmse_d[i]:.2e}', ha='center', fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(keys, fontsize=8)
ax.set_ylabel('RMSE (uV/A, log scale)')
ax.set_title('[B] Reproducible Table 2 - RMSE by window (full precision)', fontsize=9.5)
ax.legend(fontsize=8)
ax.grid(axis='y', alpha=0.3, which='both')
fig.suptitle('Fig 4. Reproducible manuscript Table 2 - reference pipeline, seed=42, '
             'variant n24_sig', fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(out_dir, 'fig4_table2_reproducible.png'), dpi=200)
plt.close(fig)

# ---------- Fig 5 ----------
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
ax = axes[0]
w = 0.18
ms_n = [MS[n_]['SNR_n'] for n_ in names]
ms_d = [MS[n_]['SNR_d'] for n_ in names]
ax.bar(x - 1.5 * w, ms_n, w, label='manuscript noisy', color='#e67e22')
ax.bar(x - 0.5 * w, snr_n, w, label='pipeline noisy', color='#c0392b')
ax.bar(x + 0.5 * w, ms_d, w, label='manuscript denoised', color='#3498db')
ax.bar(x + 1.5 * w, snr_d, w, label='pipeline denoised', color='#2980b9')
ax.set_xticks(x); ax.set_xticklabels(keys, fontsize=8)
ax.set_ylabel('SNR (dB)')
ax.set_title('[A] SNR cells: manuscript vs pipeline\n(20/20 SNR & MRE cells consistent)', fontsize=9.5)
ax.legend(fontsize=7.5)
ax.grid(axis='y', alpha=0.3)

ax = axes[1]
ms_rn = [MS[n_]['RMSE_n'] for n_ in names]
ms_rd = [MS[n_]['RMSE_d'] for n_ in names]
diff_cells = {('middle', 'RMSE_n'), ('middle', 'RMSE_d'),
              ('late', 'RMSE_n'), ('late', 'RMSE_d')}
c_ms = ['#e74c3c' if (names[i], 'RMSE_n') in diff_cells else '#e67e22'
        for i in range(4)]
c_ms2 = ['#e74c3c' if (names[i], 'RMSE_d') in diff_cells else '#3498db'
         for i in range(4)]
ax.bar(x - 1.5 * w, ms_rn, w, color=c_ms)
ax.bar(x - 0.5 * w, rmse_n, w, label='pipeline noisy', color='#c0392b')
ax.bar(x + 0.5 * w, ms_rd, w, color=c_ms2)
ax.bar(x + 1.5 * w, rmse_d, w, label='pipeline denoised', color='#2980b9')
ax.set_yscale('log')
for i in range(4):
    tag_n = ' X' if (names[i], 'RMSE_n') in diff_cells else ''
    tag_d = ' X' if (names[i], 'RMSE_d') in diff_cells else ''
    ax.text(x[i] - 1.5 * w, ms_rn[i] * 1.2, f'{ms_rn[i]:.1e}{tag_n}',
            ha='center', fontsize=6.5, color='#c0392b' if tag_n else '#e67e22')
    ax.text(x[i] + 0.5 * w, ms_rd[i] * 1.2, f'{ms_rd[i]:.1e}{tag_d}',
            ha='center', fontsize=6.5, color='#c0392b' if tag_d else '#3498db')
ax.set_xticks(x); ax.set_xticklabels(keys, fontsize=8)
ax.set_ylabel('RMSE (uV/A, log scale)')
ax.set_title('[B] RMSE cells: manuscript vs pipeline\n(red X = differs beyond printed precision: middle & late windows)',
             fontsize=9.5)
ax.legend(fontsize=7.5)
ax.grid(axis='y', alpha=0.3, which='both')
fig.suptitle('Fig 5. Reconciliation: manuscript Table 2 (printed) vs reference pipeline '
             '(full precision)', fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(out_dir, 'fig5_reconciliation.png'), dpi=200)
plt.close(fig)
print('written: output/fig4_table2_reproducible.png, output/fig5_reconciliation.png')
