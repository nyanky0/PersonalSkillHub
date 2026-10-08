// Merge multiple meeting notes into one structured docx
// Helpers: h1/h2/h3, p, bullet, bulletRich, table, cell, cellMulti, page break, header/footer
// Verified 2026-09-08: 4 source docx → 12-page output, US Letter
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, AlignmentType, ShadingType, BorderStyle, PageBreak, Header, Footer, PageNumber,
} = require('docx');
const fs = require('fs');

const FONT = 'Calibri';
const BORDER = { style: BorderStyle.SINGLE, size: 1, color: 'BFBFBF' };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: FONT, size: 32, bold: true, color: '1e3a5f' })],
    spacing: { before: 360, after: 160 },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: '2563eb' })],
    spacing: { before: 280, after: 120 },
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, font: FONT, size: 23, bold: true, color: '475569' })],
    spacing: { before: 200, after: 80 },
  });
}
function p(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: FONT, size: 21 })],
    spacing: { after: 80 },
  });
}
function bullet(text, level = 0) {
  const indent = level === 0 ? 720 : 1080 + level * 360;
  return new Paragraph({
    children: [new TextRun({ text: '•  ', font: FONT, size: 21 }),
               new TextRun({ text, font: FONT, size: 21 })],
    spacing: { after: 60, line: 276 },
    indent: { left: indent, hanging: 280 },
  });
}
function bulletRich(runs, level = 0) {
  const indent = level === 0 ? 720 : 1080 + level * 360;
  return new Paragraph({
    children: [new TextRun({ text: '•  ', font: FONT, size: 21 }),
               ...runs.map(r => new TextRun({ font: FONT, size: 21, ...r }))],
    spacing: { after: 60, line: 276 },
    indent: { left: indent, hanging: 280 },
  });
}
function cell(text, opts = {}) {
  const { bold = false, shading = null, width = null, fontSize = 20 } = opts;
  return new TableCell({
    ...(width ? { width: { size: width, type: WidthType.DXA } } : {}),
    ...(shading ? { shading: { type: ShadingType.CLEAR, fill: shading } } : {}),
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({
      children: [new TextRun({ text, font: FONT, size: fontSize, bold })],
    })],
  });
}
function cellMulti(arr, opts = {}) {
  const { bold = false, shading = null, width = null, fontSize = 20 } = opts;
  return new TableCell({
    ...(width ? { width: { size: width, type: WidthType.DXA } } : {}),
    ...(shading ? { shading: { type: ShadingType.CLEAR, fill: shading } } : {}),
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: arr.map(line => new Paragraph({
      children: [new TextRun({ text: line, font: FONT, size: fontSize, bold })],
    })),
  });
}
function table(rows, columnWidths) {
  return new Table({
    columnWidths,
    width: { size: columnWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    rows: rows.map(r => new TableRow({ children: r })),
  });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ─── Build children array ─────────────────────────────────
const children = [];

// Cover page
children.push(new Paragraph({ children: [], spacing: { before: 4000 } }));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: 'NOTES DISKUSI BLUEPRINT', font: FONT, size: 40, bold: true, color: '1e3a5f' })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: 'Project IBT — Web Request Fulfillment (SAP B1 Integration)', font: FONT, size: 26, color: '475569' })],
  spacing: { after: 400 },
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: 'Gabungan Sesi: 01, 02 & 04 September 2026', font: FONT, size: 24, color: '475569' })],
}));
children.push(pageBreak());

// Metadata table
children.push(table([
  [cell('Tanggal', { bold: true, shading: 'D9E2F3', width: 2400 }),
   cellMulti(['Senin, 01 September 2026', 'Rabu, 02 September 2026', 'Jumat, 04 September 2026'], { width: 6960 })],
  [cell('Topik', { bold: true, shading: 'D9E2F3', width: 2400 }),
   cell('Blueprint fitur Request Fulfillment, katalog item, approval, template transaksi, alur RL & PQC, history log, batasan akses user, flow AS-IS', { width: 6960 })],
  [cell('Peserta', { bold: true, shading: 'D9E2F3', width: 2400 }),
   cell('Tim IBT, Customer, PM, Fleet Department', { width: 6960 })],
], [2400, 6960]));

// ─── SECTIONS ─────────────────────────────────────────────
// Add sections here using h1/h2/h3/bullet/table helpers
// children.push(h1('1. ...'));
// children.push(h2('1.1 ...'));
// children.push(bullet('...'));

// ─── Consolidated tables at end ───────────────────────────
// Open questions table + Action items table (merged from all sources, renumbered)

// ─── Build Document ───────────────────────────────────────
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: FONT, size: 21 },
        paragraph: { spacing: { after: 80 } },
      },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 }, // US Letter
        margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: 'IBT — Blueprint Notes | September 2026', font: FONT, size: 16, color: '808080', italics: true })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: 'Halaman ', font: FONT, size: 16, color: '808080' }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: '808080' }),
            new TextRun({ text: ' dari ', font: FONT, size: 16, color: '808080' }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: '808080' }),
          ],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  const out = '/path/to/output/Gabungan Notes Blueprint - September 2026.docx';
  fs.writeFileSync(out, buf);
  console.log('DONE: ' + out);
  console.log('Size: ' + (buf.length / 1024).toFixed(1) + ' KB');
});
