# Reproducibility Pack v3 — TEM Denoising Reference Pipeline & Reproducible Table 2

**Prepared for**: zhaoyangyang@92xueshu.com
**Date**: 2026-09-30 (v3; supersedes v2 and v1 of the same day)
**License**: CC BY 4.0 (see LICENSE) | **Citation**: see CITATION.cff
**Companion documents**:
- APR Review Report R4, `APR评审报告_R4_含水构造TEM论文_20260930.docx`
- Terminal-round revision task book, `修改任务书_含水构造TEM论文_终稿轮_20260930.docx`

---

## 1. Is this pack complete?

Mapped against the repository minimum requirements in the revision task book
(Section 4):

| # | requirement | status in this pack |
|---|---|---|
| 4.1 | ownership & OSI license | **YES** — LICENSE (CC BY 4.0), CITATION.cff, attribution statements |
| 4.2 | full workflow: forward / noise+denoise / mapping / inversion / reconstruction / evaluation | **evaluation: YES** (Eqs. 9–11, four windows, MC60) — **noise+denoise: reference implementation** (improved threshold is the parameterized literature form, not the authors' undisclosed function) — **forward / mapping / inversion / reconstruction: NO, and cannot be** — see `GAPS.md` for the exact missing parameters and who must supply them |
| 4.3 | numeric reconciliation, full precision, one pipeline | **YES** — `output/table2_reproducible_full_precision.csv`, `output/table2_reconciliation_vs_manuscript.csv`, identity closure on all four windows |
| 4.4 | archival: versioned DOI, environment, seeds | **PARTIAL** — environment pinned (`requirements.txt`, tested on Python 3.12.3), seed=42 throughout, run order in `run_all.sh`; the versioned DOI must come from the authors' own archive (this pack is email-distributed review material, not the authors' repository) |
| 4.5 | removal of the currently cited repository as source | this pack never cites that repository as its source and is independent of it |

**Bottom line**: this pack is **complete as a review-side reference
repository** — every number it produces is one-command reproducible at full
precision with a stated provenance. It is **not, and cannot become, the
authors' official repository**: the 3-D forward model, the Eq. (7)
time-frequency mapping with its phase construction, the Eq. (8) inversion,
the IDW 3-D reconstruction and the authors' raw field data exist only on the
authors' side. `GAPS.md` is the build checklist for that repository.

## 2. What is new in v3 (vs v2)

1. `src/10_mc_robustness.py` — Monte-Carlo, 60 realisations: the
   distribution statistics behind manuscript Table 3. Result:
   E[ΔSNR_all] = **+0.34 ± 2.83 dB**, P(ΔSNR>3 dB) = **0.117**,
   P(ΔSNR<0) = 0.43 — consistent with the revision's printed +0.36 ± 2.89 /
   P=0.15 within Monte-Carlo variation (different seed stream, 1001–1060).
2. `src/11_additive_noise_control.py` — the additive-noise control required
   by task T6. Headline: the +20.31 dB late-window gain survives only under
   the manuscript's pure signal-scaled noise model (A0); in the realistic
   combined case (σ=0.24|s| + additive floor 1e-3·peak) the reference
   pipeline is net-negative on early gates and near-neutral elsewhere.
3. All three noise variants now carry denoised + metrics outputs
   (`n5_sig`, `n5_fs`, `n24_sig`). Note the honest behavior at low noise:
   at n5_sig the threshold pipeline *degrades* the all-window SNR
   (28.84 → 23.77 dB) — Rigrsure over-shrinks when noise is weak.
4. Figures `fig6_mc60.png`, `fig7_additive.png`; document
   `review_figures_v3.docx` (all 7 figures + data tables).
5. Repository infrastructure: `LICENSE`, `CITATION.cff`,
   `requirements.txt` (pinned), `run_all.sh` (one-click reproduction),
   `GAPS.md` (gap manifest).

v1/v2 outputs are retained unchanged; all additions are computed from the
same seed-42 arrays.

## 3. The reproducible Table 2 (full precision, reference pipeline)

variant `n24_sig`, improved soft-threshold denoising:

| window | gates | SNR noisy (dB) | SNR denoised (dB) | ΔSNR (dB) | RMSE noisy (µV/A) | RMSE denoised (µV/A) | MRE noisy (%) | MRE denoised (%) | identity gap (dB) |
|---|---|---|---|---|---|---|---|---|---|
| early | 1–12 | 17.9220 | 19.3019 | +1.380 | 2.7042e-02 | 2.3070e-02 | 28.70 | 13.30 | +0.000000 ✓ |
| middle | 13–28 | 14.8733 | 24.8194 | +9.946 | 2.5413e-04 | 8.0863e-05 | 40.50 | 8.45 | −0.000000 ✓ |
| late | 29–40 | 11.6719 | 31.9799 | +20.308 | 6.3822e-07 | 6.1598e-08 | 41.46 | 15.49 | +0.000000 ✓ |
| all | 1–40 | 17.9217 | 19.3021 | +1.380 | 1.4812e-02 | 1.2636e-02 | 41.46 | 15.49 | −0.000000 ✓ |

Reconciliation against the manuscript print: 20/24 cells consistent; the 4
differing cells are exactly the middle/late RMSE values (manuscript
3.32e-04/1.04e-04, 3.27e-07/8.95e-08 vs pipeline 2.5413e-04/8.0863e-05,
6.3822e-07/6.1598e-08). No single pipeline can reproduce both sets —
reprint Table 2 from one rerun pipeline with a provenance statement (task T1).

## 4. How to reproduce

```bash
bash run_all.sh          # everything, in order, deterministic (seed 42)
```

or run the scripts in `src/` individually: 01 → 02 (×3 variants) → 03 (×3)
→ 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13.
Requirements: Python 3.12, packages pinned in `requirements.txt`.

## 5. What this pack is (and is not)

Review-side **reference implementation** built only from manuscript-disclosed
parameters. NOT: the authors' raw data (synthetic, seed 42); the authors' 3-D
forward model, Eq. (7) mapping, Eq. (8) inversion or IDW reconstruction
(undisclosed — `GAPS.md`); a substitute for the authors' own versioned-DOI
repository (task T2). The "improved" soft threshold is the parameterized
literature form (β=2.0) pending the authors' exact function.

## 6. Package contents

```
tem_repro_pack_v3/
├── README.md            (this file)      LICENSE          (CC BY 4.0)
├── CITATION.cff                          requirements.txt (pinned)
├── run_all.sh           (one-click)      GAPS.md          (gap manifest)
├── data/                seed-42 synthetic data (all 3 variants + denoised 40-gate tables)
├── src/
│   01_make_synthetic_data.py   02_denoise_wavelet.py    03_evaluate_metrics.py
│   04_audit_manuscript_table2.py   05_make_figures.py   06_build_figures_docx.py
│   07_reproducible_table2.py   08_figures_v2.py         09_build_docx_v2.py
│   10_mc_robustness.py         11_additive_noise_control.py
│   12_figures_v3.py            13_build_docx_v3.py
└── output/
    ├── metrics_{n24_sig,n5_sig,n5_fs}.csv          audit_report_manuscript_table2.txt
    ├── fig1..fig3 (v1, unchanged)                  review_figures.docx (v1)
    ├── table2_reproducible_full_precision.csv      table2_reconciliation_vs_manuscript.csv
    ├── table2_identity_check.txt                   fig4_table2_reproducible.png
    ├── fig5_reconciliation.png                     review_figures_v2.docx
    ├── table3_mc60_full_precision.csv              table3_mc60_summary.txt
    ├── additive_control_full_precision.csv         additive_control_summary.txt
    ├── fig6_mc60.png                               fig7_additive.png
    └── review_figures_v3.docx   (7 figures + data tables)
```
