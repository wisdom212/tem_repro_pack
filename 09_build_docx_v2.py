# -*- coding: utf-8 -*-
"""Build output/review_figures_v2.docx - all figures + their data tables."""
import csv
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, '..', 'data')
out_dir = os.path.join(here, '..', 'output')
VARIANT = 'n24_sig'

doc = Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(10)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def set_cn(run, cn='宋体', en='Times New Roman'):
    run.font.name = en
    run.element.rPr.rFonts.set(qn('w:eastAsia'), cn)


def para(text, bold=False, size=10, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    set_cn(r)
    if align:
        p.alignment = align
    return p


def table(headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htext in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ''
        r = c.paragraphs[0].add_run(htext)
        r.bold = True
        r.font.size = Pt(8)
        set_cn(r, '黑体')
        tcPr = c._tc.get_or_add_tcPr()
        shd = tcPr.makeelement(qn('w:shd'), {qn('w:val'): 'clear', qn('w:fill'): 'D9E2F3'})
        tcPr.append(shd)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.rows[ri + 1].cells[ci]
            c.text = ''
            r = c.paragraphs[0].add_run(str(val))
            r.font.size = Pt(7.5)
            set_cn(r)
    return t


def figure(png, width_cm, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(os.path.join(out_dir, png), width=Cm(width_cm))
    para(caption, bold=True, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)


# ================= title =================
para('Reproducibility Pack v2 - Figures and Data Tables', bold=True, size=15,
     align=WD_ALIGN_PARAGRAPH.CENTER)
para('TEM denoising reference pipeline & reproducible manuscript Table 2', size=11,
     align=WD_ALIGN_PARAGRAPH.CENTER)
para('variant: n24_sig | seed: 42 | 2026-09-30 (pack v2, companion to the R4 '
     'review report and the terminal-round revision task book)', size=9,
     align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_paragraph()

# ================= Fig 1 =================
figure('fig1_decay.png', 14.5,
       'Fig 1. Synthetic TEM decay curve and reference denoising result '
       '(sym8 / 5-level / Rigrsure; denoising on the 2048-point time series, '
       'then gated to 40 windows)')
rows = []
with open(os.path.join(data_dir, f'denoised_{VARIANT}.csv')) as f:
    for row in csv.DictReader(f):
        rows.append([f"{float(row['t_center_ms']):.3f}",
                     f"{float(row['clean_uVA']):.4e}",
                     f"{float(row['noisy_uVA']):.4e}",
                     f"{float(row['denoised_improved_uVA']):.4e}",
                     f"{float(row['denoised_soft_uVA']):.4e}"])
para('Data table for Fig 1 (40 gates; uV/A)', bold=True, size=9)
table(['t_center (ms)', 'clean', 'noisy (24% signal-scaled)',
       'denoised (improved)', 'denoised (classical soft)'], rows)
doc.add_page_break()

# ================= Fig 2 =================
figure('fig2_metrics.png', 16.5,
       'Fig 2. Recomputed quality metrics by window (SNR / RMSE / MRE), '
       'reference pipeline, n24_sig noise')
rows = []
with open(os.path.join(out_dir, f'metrics_{VARIANT}.csv')) as f:
    rd = list(csv.reader(f))
for r in rd[1:]:
    rows.append(r)
para('Data table for Fig 2 (display rounding: SNR 2 dp, RMSE 4 dp, MRE 2 dp; '
     'full precision in Table 2 of this document)', bold=True, size=9)
table(['variant', 'window', 'state', 'SNR_dB', 'RMSE_uVA', 'MRE_pct'], rows)
doc.add_page_break()

# ================= Fig 3 =================
figure('fig3_audit.png', 16.0,
       'Fig 3. Arithmetic audit of the ORIGINAL (R1/R2) manuscript Table 2 '
       '(numbers taken from the manuscript; no model re-run) - retained '
       'unchanged from pack v1 for traceability')
table(['check', 'window', 'manuscript', 'recomputed / implied', 'delta'],
      [['[A] window-weighted RMSE aggregation (all window)',
        '-', 'noisy 0.142 / denoised 0.015', 'noisy 0.180 / denoised 0.0235',
        'inconsistent'],
       ['[B] SNR-gain vs RMSE-ratio identity', 'early', 'reported 12.30 dB',
        'implied 17.50 dB', '-5.20 dB'],
       ['[B] SNR-gain vs RMSE-ratio identity', 'middle', 'reported 14.20 dB',
        'implied 17.79 dB', '-3.59 dB'],
       ['[B] SNR-gain vs RMSE-ratio identity', 'late', 'reported 17.30 dB',
        'implied 21.37 dB', '-4.07 dB'],
       ['[B] SNR-gain vs RMSE-ratio identity', 'all', 'reported 16.30 dB',
        'implied 19.52 dB', '-3.22 dB'],
       ['[C] noise implied by reported noisy SNR', 'all', 'claimed 5% Gaussian',
        'implied 24.0% of signal amplitude', 'inconsistent']])
doc.add_page_break()

# ================= Fig 4 =================
figure('fig4_table2_reproducible.png', 16.5,
       'Fig 4. REPRODUCIBLE manuscript Table 2 - full-precision output of the '
       'reference pipeline (this is the v2 deliverable for review Task T1)')
rows = []
with open(os.path.join(out_dir, 'table2_reproducible_full_precision.csv')) as f:
    rd = list(csv.reader(f))
for r in rd[1:]:
    rows.append(r)
para('Reproducible Table 2 (full precision)', bold=True, size=9)
table(['window', 'gates', 'state', 'SNR_dB', 'RMSE_uVA', 'MRE_pct / check'],
      rows)
doc.add_page_break()

# ================= Fig 5 =================
figure('fig5_reconciliation.png', 16.5,
       'Fig 5. Reconciliation - manuscript printed Table 2 (R3/R4 revision) '
       'vs reference pipeline: 20/24 cells consistent; the 4 differing cells '
       'are exactly the middle/late RMSE values')
rows = []
with open(os.path.join(out_dir, 'table2_reconciliation_vs_manuscript.csv')) as f:
    rd = list(csv.reader(f))
for r in rd[1:]:
    rows.append(r)
para('Data table for Fig 5 (cell-by-cell reconciliation)', bold=True, size=9)
table(['window', 'cell', 'manuscript printed', 'reference pipeline',
       'abs delta', 'consistent'], rows)

out = os.path.join(out_dir, 'review_figures_v2.docx')
doc.save(out)
print('saved:', out, os.path.getsize(out), 'bytes')
