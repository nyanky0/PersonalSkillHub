"""
Helper gaya dokumen Word untuk laporan IBT Suite — rombak v1.5.

Dipakai oleh script build_*.py di folder yang sama:

    from word_style import Doc

    d = Doc("Judul", "Subjudul", "Laporan Teknis")
    d.h1("Bab 1")
    d.p("Paragraf...")
    d.table(["Kolom A", "Kolom B"], [["a", "b"]], widths=[3.0, 9.0])
    d.save("path.docx")

Semua warna memakai palet produk (biru IBT) supaya konsisten dengan aplikasi.
"""

from __future__ import annotations

from datetime import datetime

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# ── palet ─────────────────────────────────────────────────────────────────────
IBT_BLUE = RGBColor(0x0E, 0x5A, 0xA8)
IBT_BLUE_HEX = "0E5AA8"
IBT_DARK = RGBColor(0x0F, 0x2A, 0x43)
TEAL_HEX = "0F766E"
SLATE = RGBColor(0x47, 0x55, 0x69)
SLATE_LIGHT = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

OK_HEX = "DCFCE7"
WARN_HEX = "FEF3C7"
BAD_HEX = "FEE2E2"
INFO_HEX = "E0F2FE"
ZEBRA_HEX = "F1F5F9"

FONT = "Segoe UI"


def _shade(cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _cell_margins(table) -> None:
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", 60), ("left", 110), ("bottom", 60), ("right", 110)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tbl_pr.append(mar)


def _field(paragraph, instr: str) -> None:
    """Sisipkan field Word (PAGE / NUMPAGES)."""
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_end)


class Doc:
    def __init__(self, title: str, subtitle: str, kind: str = "Laporan Teknis", author: str = "IBT Suite — Tim Pengembang Web App"):
        self.doc = Document()
        self.title = title
        self._base_style()
        self._page_setup()
        self._cover(title, subtitle, kind, author)

    # ── setup ────────────────────────────────────────────────────────────────
    def _base_style(self) -> None:
        st = self.doc.styles["Normal"]
        st.font.name = FONT
        st.font.size = Pt(10)
        st.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.15
        rpr = st.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), FONT)
        rfonts.set(qn("w:cs"), FONT)

        for name, size, color, bold, before, after in (
            ("Heading 1", 17, IBT_BLUE, True, 16, 6),
            ("Heading 2", 13, IBT_DARK, True, 12, 4),
            ("Heading 3", 11, SLATE, True, 9, 3),
        ):
            s = self.doc.styles[name]
            s.font.name = FONT
            s.font.size = Pt(size)
            s.font.color.rgb = color
            s.font.bold = bold
            s.paragraph_format.space_before = Pt(before)
            s.paragraph_format.space_after = Pt(after)
            s.paragraph_format.keep_with_next = True

    def _page_setup(self) -> None:
        sec = self.doc.sections[0]
        sec.top_margin = Cm(2.2)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.3)
        sec.right_margin = Cm(2.0)
        self.usable_cm = 21.0 - 2.3 - 2.0  # A4 - margin

    def _footer(self) -> None:
        sec = self.doc.sections[0]
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("IBT Suite — " + self.title + "  |  halaman ")
        run.font.size = Pt(8)
        run.font.color.rgb = SLATE_LIGHT
        _field(p, "PAGE")
        r2 = p.add_run(" dari ")
        r2.font.size = Pt(8)
        r2.font.color.rgb = SLATE_LIGHT
        _field(p, "NUMPAGES")
        for r in p.runs:
            r.font.name = FONT
            r.font.size = Pt(8)
            r.font.color.rgb = SLATE_LIGHT

    def _cover(self, title: str, subtitle: str, kind: str, author: str) -> None:
        for _ in range(3):
            self.doc.add_paragraph()
        p = self.doc.add_paragraph()
        r = p.add_run("IBT SUITE  ·  " + kind.upper())
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = IBT_BLUE
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        p = self.doc.add_paragraph()
        r = p.add_run(title)
        r.font.size = Pt(28)
        r.font.bold = True
        r.font.color.rgb = IBT_DARK
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)

        p = self.doc.add_paragraph()
        r = p.add_run(subtitle)
        r.font.size = Pt(12)
        r.font.color.rgb = SLATE
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(18)

        t = self.doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t.rows[0].cells[0]
        _shade(cell, IBT_BLUE_HEX)
        cell.text = ""
        cp = cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cp.add_run("PT Indobaruna Bulk Transport  —  IBT Suite v2.4 (Web App Laravel + React/Inertia)")
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = WHITE

        meta = self.doc.add_paragraph()
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta.paragraph_format.space_before = Pt(16)
        r = meta.add_run(
            f"Disusun oleh: {author}\n"
            f"Tanggal: {datetime.now().strftime('%d %B %Y')}\n"
            "Basis kode: branch release/v1.4.0 · database IBTWEBAPP · SAP B1 Service Layer"
        )
        r.font.size = Pt(9)
        r.font.color.rgb = SLATE_LIGHT

        self.doc.add_paragraph()
        self._footer()

    # ── konten ───────────────────────────────────────────────────────────────
    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def h1(self, text: str):
        self.doc.add_heading(text, level=1)
        self._rule()

    def h2(self, text: str):
        self.doc.add_heading(text, level=2)

    def h3(self, text: str):
        self.doc.add_heading(text, level=3)

    def _rule(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p_pr = p._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "10")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), IBT_BLUE_HEX)
        borders.append(bottom)
        p_pr.append(borders)

    def p(self, text: str, italic: bool = False, size: int = 10):
        par = self.doc.add_paragraph()
        for i, chunk in enumerate(str(text).split("**")):
            if not chunk:
                continue
            r = par.add_run(chunk)
            r.font.size = Pt(size)
            r.font.italic = italic
            r.font.bold = i % 2 == 1
        return par

    def bullets(self, items, level: int = 0):
        for it in items:
            par = self.doc.add_paragraph(style="List Bullet")
            par.paragraph_format.left_indent = Cm(0.6 + level * 0.5)
            par.paragraph_format.space_after = Pt(2)
            for i, chunk in enumerate(str(it).split("**")):
                if not chunk:
                    continue
                r = par.add_run(chunk)
                r.font.size = Pt(10)
                r.font.bold = i % 2 == 1

    def numbered(self, items):
        for it in items:
            par = self.doc.add_paragraph(style="List Number")
            par.paragraph_format.space_after = Pt(2)
            for i, chunk in enumerate(str(it).split("**")):
                if not chunk:
                    continue
                r = par.add_run(chunk)
                r.font.size = Pt(10)
                r.font.bold = i % 2 == 1

    def table(self, headers, rows, widths=None, zebra: bool = True, status_col: int | None = None, font_size: int = 8.5):
        t = self.doc.add_table(rows=1, cols=len(headers))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        _cell_margins(t)

        hdr = t.rows[0]
        for i, h in enumerate(headers):
            cell = hdr.cells[i]
            cell.text = ""
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            r = par.add_run(str(h))
            r.font.bold = True
            r.font.size = Pt(font_size)
            r.font.color.rgb = WHITE
            _shade(cell, IBT_BLUE_HEX)

        for idx, row in enumerate(rows):
            cells = t.add_row().cells
            for i, val in enumerate(row):
                cell = cells[i]
                cell.text = ""
                par = cell.paragraphs[0]
                par.paragraph_format.space_after = Pt(0)
                text = "" if val is None else str(val)
                bold = text.startswith("**") and text.endswith("**")
                if bold:
                    text = text.strip("*")
                r = par.add_run(text)
                r.font.size = Pt(font_size)
                r.font.bold = bold
                if status_col is not None and i == status_col:
                    upper = text.upper()
                    if any(k in upper for k in ("SELESAI", "SUDAH", "ADA", "OK", "PASS")):
                        _shade(cell, OK_HEX)
                    elif any(k in upper for k in ("BELUM", "KURANG", "GAGAL", "MISMATCH")):
                        _shade(cell, BAD_HEX)
                    elif any(k in upper for k in ("SEBAGIAN", "PARSIAL", "SELISIH", "PERLU", "OPSIONAL")):
                        _shade(cell, WARN_HEX)
                if zebra and idx % 2 == 1 and not (status_col is not None and i == status_col):
                    _shade(cell, ZEBRA_HEX)

        if widths:
            for row in t.rows:
                for i, w in enumerate(widths):
                    if i < len(row.cells):
                        row.cells[i].width = Cm(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def callout(self, title: str, text: str, kind: str = "info"):
        fill = {"info": INFO_HEX, "ok": OK_HEX, "warn": WARN_HEX, "bad": BAD_HEX}.get(kind, INFO_HEX)
        t = self.doc.add_table(rows=1, cols=1)
        cell = t.rows[0].cells[0]
        cell.text = ""
        _shade(cell, fill)
        par = cell.paragraphs[0]
        par.paragraph_format.space_after = Pt(0)
        r = par.add_run(title + " — ")
        r.font.bold = True
        r.font.size = Pt(9)
        r2 = par.add_run(text)
        r2.font.size = Pt(9)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def toc(self, items):
        """Daftar isi manual (tanpa field, selalu terlihat tanpa perlu F9)."""
        for it in items:
            par = self.doc.add_paragraph()
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.left_indent = Cm(0.0 if not str(it).startswith("   ") else 0.6)
            r = par.add_run(str(it).strip())
            r.font.size = Pt(10)
            r.font.color.rgb = IBT_DARK if not str(it).startswith("   ") else SLATE
            r.font.bold = not str(it).startswith("   ")

    def save(self, path: str):
        self.doc.save(path)
        return path
