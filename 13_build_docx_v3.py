# -*- coding: utf-8 -*-
"""Step 13: Build output/review_figures_v3.docx = v2 docx + figs 6-7."""
import csv
import os
import shutil
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(here, '..', 'output')

# start from v2 document and append v3 sections
src_docx = os.path.join(out_dir, 'review_figures_v2.docx')
out_docx = os.path.join(out_dir, 'review_figures_v3.docx')
shutil.copy(src_docx, out_docx)

doc = Document(out_docx)
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


doc.add_page_break()
para('v3 addendum (pack v3, 2026-09-30)', bold=True, size=13,
     align=WD_ALIGN_PARAGRAPH.CENTER)
para('Monte-Carlo robustness (Table 3 provenance) and additive-noise control '
     '(task T6), with their data tables.', size=9.5,
     align=WD_ALIGN_PARAGRAPH.CENTER)

# ---- Fig 6 ----
figure('fig6_mc60.png', 16.0,
       'Fig 6. Monte-Carlo robustness, 60 realisations (seeds 1001-1060): '
       'the quoted +1.38 dB all-window gain is one draw, not the expectation')
rows = []
with open(os.path.join(out_dir, 'table3_mc60_full_precision.csv')) as f:
    for r in csv.DictReader(f):
        rows.append([r['seed'], r['dSNR_early_dB'], r['dSNR_middle_dB'],
                     r['dSNR_late_dB'], r['dSNR_all_dB']])
para('Data table for Fig 6 (per-seed ΔSNR, dB)', bold=True, size=9)
table(['seed', 'early', 'middle', 'late', 'all'], rows)
doc.add_paragraph()
with open(os.path.join(out_dir, 'table3_mc60_summary.txt')) as f:
    para('Summary (table3_mc60_summary.txt): ' + f.read().replace('\n', ' | '),
         size=8.5)
doc.add_page_break()

# ---- Fig 7 ----
figure('fig7_additive.png', 16.0,
       'Fig 7. Additive background-noise control: the +20.31 dB late-window '
       'gain exists only under the manuscript pure signal-scaled noise model '
       '(A0); under a realistic combined model (A2c) the pipeline is '
       'net-negative on early gates and near-neutral elsewhere')
rows = []
with open(os.path.join(out_dir, 'additive_control_full_precision.csv')) as f:
    for r in csv.DictReader(f):
        rows.append([r['case'], r['window'], r['SNR_noisy_dB'],
                     r['SNR_denoised_dB'], r['dSNR_dB'], r['RMSE_noisy_uVA'],
                     r['RMSE_denoised_uVA']])
para('Data table for Fig 7 (full precision)', bold=True, size=9)
table(['case', 'window', 'SNR noisy (dB)', 'SNR denoised (dB)', 'ΔSNR (dB)',
       'RMSE noisy (µV/A)', 'RMSE denoised (µV/A)'], rows)

doc.save(out_docx)
print('saved:', out_docx, os.path.getsize(out_docx), 'bytes')
