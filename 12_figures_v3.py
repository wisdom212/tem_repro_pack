# -*- coding: utf-8 -*-
"""Step 12: Figures v3 - MC60 robustness + additive-noise control."""
import numpy as np
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(here, '..', 'output')

# ---------- Fig 6: MC60 ----------
seeds, d_all = [], []
with open(os.path.join(out_dir, 'table3_mc60_full_precision.csv')) as f:
    for row in csv.DictReader(f):
        seeds.append(int(row['seed']))
        d_all.append(float(row['dSNR_all_dB']))
a = np.array(d_all)

fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.0))
ax = axes[0]
ax.hist(a, bins=12, color='#2980b9', edgecolor='white')
ax.axvline(a.mean(), color='#c0392b', lw=2,
           label=f'mean = {a.mean():+.2f} dB')
ax.axvline(0.0, color='black', lw=1, ls='--')
ax.axvline(3.0, color='#8e44ad', lw=1.5, ls=':',
           label='single-draw gain quoted in manuscript (+1.38 dB)')
ax.set_xlabel('all-window ΔSNR (dB), 60 realisations')
ax.set_ylabel('count')
ax.set_title('[A] Distribution of the all-window SNR gain\n'
             'reference pipeline, σ=0.24|s|', fontsize=9.5)
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

ax = axes[1]
parts = ax.violinplot(a, showmeans=True, showmedians=True)
for pc in parts['bodies']:
    pc.set_facecolor('#85c1e9')
    pc.set_edgecolor('#2471a3')
ax.axhline(0, color='black', lw=1, ls='--')
ax.set_xticks([1])
ax.set_xticklabels(['all window'])
ax.set_ylabel('ΔSNR (dB)')
ax.set_title(f'[B] E = {a.mean():+.2f} ± {a.std(ddof=1):.2f} dB | '
             f'P(ΔSNR>3 dB) = {(a > 3).mean():.2f} | '
             f'P(ΔSNR<0) = {(a < 0).mean():.2f}', fontsize=9.5)
ax.grid(axis='y', alpha=0.3)
fig.suptitle('Fig 6. Monte-Carlo robustness (60 realisations, seeds 1001-1060) - '
             'manuscript Table 3 provenance', fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(out_dir, 'fig6_mc60.png'), dpi=200)
plt.close(fig)

# ---------- Fig 7: additive-noise control ----------
cases = []
data = {}
with open(os.path.join(out_dir, 'additive_control_full_precision.csv')) as f:
    for row in csv.DictReader(f):
        c = row['case']
        if c not in data:
            data[c] = {}
            cases.append(c)
        data[c][row['window']] = float(row['dSNR_dB'])

wins = ['early', 'middle', 'late', 'all']
labels = [c.replace('_', '\n') for c in cases]
x = np.arange(len(cases))
fig, ax = plt.subplots(figsize=(9.5, 4.3))
w = 0.2
colors = {'early': '#e67e22', 'middle': '#2980b9', 'late': '#8e44ad',
          'all': '#16a085'}
for i, win in enumerate(wins):
    vals = [data[c][win] for c in cases]
    ax.bar(x + (i - 1.5) * w, vals, w, label=win, color=colors[win])
ax.axhline(0, color='black', lw=1)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=7.5)
ax.set_ylabel('ΔSNR (dB)')
ax.set_title('Fig 7. Additive background-noise control (task T6): denoiser gain '
             'by noise model\nA0 = manuscript assumption (signal-scaled only); '
             'A1-A3 = additive floor at 1e-2/1e-3/1e-4 of peak; '
             'A2c = realistic combined case', fontsize=9)
ax.legend(fontsize=8, ncol=4)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(out_dir, 'fig7_additive.png'), dpi=200)
plt.close(fig)
print('written: output/fig6_mc60.png, output/fig7_additive.png')
