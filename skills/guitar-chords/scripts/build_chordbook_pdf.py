#!/usr/bin/env python3
"""Build a chord-book PDF from fetched chord text files (raw/NN_<title>.txt).

Run with a venv that has reportlab (pip install reportlab pypdf).
Usage: python build_chordbook_pdf.py [raw_dir] [out.pdf]
"""
import re, os, sys, glob

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, XPreformatted,
                                Spacer, PageBreak)

RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
OUT = sys.argv[2] if len(sys.argv) > 2 else "Kumpulan_Chord_Gitar.pdf"

ACCENT = HexColor("#8B1E3F")
DARK = HexColor("#222222")

title_style = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20,
                             leading=24, textColor=ACCENT, spaceAfter=4)
artist_style = ParagraphStyle("a", fontName="Helvetica-Oblique", fontSize=12,
                              leading=16, textColor=DARK, spaceAfter=2)
src_style = ParagraphStyle("s", fontName="Helvetica", fontSize=7.5,
                           leading=10, textColor=HexColor("#888888"), spaceAfter=10)
chord_style = ParagraphStyle("c", fontName="Courier", fontSize=8.5, leading=11.5,
                             textColor=DARK)
toc_style = ParagraphStyle("toc", fontName="Helvetica", fontSize=11,
                           leading=18, textColor=DARK)

def parse_file(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    title = artist = src = ""
    body = []
    for ln in lines:
        if ln.startswith("# "):
            rest = ln[2:]
            if rest.startswith("Sumber:"):
                src = rest[8:].strip()
            elif "—" in rest:
                title, artist = [x.strip() for x in rest.split("—", 1)]
        else:
            body.append(ln.rstrip())
    return title, artist, src, "\n".join(body).replace("\r", "").strip()

files = sorted(glob.glob(os.path.join(RAW, "[0-9][0-9]_*.txt")))
songs = [parse_file(f) for f in files]
if not songs:
    sys.exit("no raw/NN_*.txt files found in " + RAW)

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Kumpulan Chord Gitar", author="Hermes Agent")

story = []
story.append(Spacer(1, 3.5*cm))
story.append(Paragraph("KUMPULAN CHORD GITAR", title_style))
story.append(Paragraph("Lirik + Kunci Gitar", artist_style))
story.append(Spacer(1, 1.2*cm))
story.append(Paragraph("DAFTAR ISI", ParagraphStyle("t2", parent=title_style, fontSize=14)))
for i, (t, a, s, _) in enumerate(songs, 1):
    story.append(Paragraph(f"{i:02d}. {t} — {a}", toc_style))
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("Sumber chord: tercantum per lagu.", src_style))
story.append(PageBreak())

for i, (t, a, s, text) in enumerate(songs, 1):
    story.append(Paragraph(f"{i:02d}. {t}", title_style))
    story.append(Paragraph(a, artist_style))
    story.append(Paragraph(f"Sumber: {s}", src_style))
    # XPreformatted preserves whitespace; Paragraph would collapse it and
    # destroy chord-over-lyric alignment. Courier keeps columns lined up.
    story.append(XPreformatted(text, chord_style))
    if i < len(songs):
        story.append(PageBreak())

doc.build(story)
print("PDF written:", OUT, os.path.getsize(OUT), "bytes")
