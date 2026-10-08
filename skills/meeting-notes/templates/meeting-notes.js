// Known-good docx-js builder for structured meeting minutes.
// Verified 2026-09-02 (IBT blueprint session). Reproduce with modifications.
// Requires: npm install docx (in any workdir).
// Usage: set OUT path + edit `children` content, then `node meeting-notes.js`.

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
} = require("docx");
const fs = require("fs");

// A4 portrait, 1" margins
const PAGE_W = 11906, MARGIN = 1440;
const CONTENT_W = PAGE_W - MARGIN * 2; // 9026 DXA

const NAVY = "1F3864", ACCENT = "2E74B5", LIGHT = "DEEBF7", GREY = "F2F2F2";
const B = (t, o = {}) => new TextRun({ text: t, bold: true, ...o });
const T = (t, o = {}) => new TextRun({ text: t, ...o });

const heading = (text, level = HeadingLevel.HEADING_1) =>
  new Paragraph({ heading: level, spacing: { before: 320, after: 120 }, children: [
    new TextRun({ text, bold: true, color: level === HeadingLevel.HEADING_1 ? NAVY : ACCENT,
      size: level === HeadingLevel.HEADING_1 ? 28 : 24 }),
  ]});

const bullet = (text, { level = 0, bold = false } = {}) =>
  new Paragraph({ bullet: { level }, spacing: { after: 80 }, children: [new TextRun({ text, bold })] });

const labelBullet = (label, rest, level = 0) =>
  new Paragraph({ bullet: { level }, spacing: { after: 80 }, children: [B(label), T(rest)] });

// decision (green) / open (yellow) / info (blue) callout — single-cell shaded table
function callout(kind, label, items) {
  const colors = { decision: ["E2EFDA", "375623"], open: ["FFF2CC", "7F6000"], info: ["DEEBF7", "1F3864"] };
  const [fill, fontColor] = colors[kind];
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [CONTENT_W],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: fontColor },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: fontColor },
      left: { style: BorderStyle.SINGLE, size: 18, color: fontColor },
      right: { style: BorderStyle.SINGLE, size: 4, color: fontColor },
      insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({ children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill },
      width: { size: CONTENT_W, type: WidthType.DXA },
      margins: { top: 100, bottom: 100, left: 160, right: 160 },
      children: [
        new Paragraph({ spacing: { after: 60 }, children: [B(label, { color: fontColor, size: 20 })] }),
        ...items.map(s => new Paragraph({ spacing: { after: 40 }, children: [T(s, { size: 20 })] })),
      ],
    })] })],
  });
}

const spacer = (h = 160) => new Paragraph({ spacing: { after: h }, children: [] });

// zebra action-items table
function actionTable(rows /* [action, status][] */) {
  const col = [700, CONTENT_W - 700 - 1600, 1600];
  const cell = (t, w, opts = {}) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    margins: { top: 50, bottom: 50, left: 120, right: 120 }, ...opts,
    children: [new Paragraph({ children: [T(t, { size: 20 })] })],
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: col,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 8, color: NAVY },
      bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
    },
    rows: [
      new TableRow({ children: ["No", "Action Item", "PIC / Status"].map((h, i) => new TableCell({
        shading: { type: ShadingType.CLEAR, fill: NAVY },
        width: { size: col[i], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [B(h, { color: "FFFFFF", size: 20 })] })],
      })) }),
      ...rows.map(([a, s], i) => new TableRow({ children: [
        cell(String(i + 1), col[0], { shading: i % 2 ? { type: ShadingType.CLEAR, fill: GREY } : undefined }),
        cell(a, col[1], { shading: i % 2 ? { type: ShadingType.CLEAR, fill: GREY } : undefined }),
        new TableCell({
          width: { size: col[2], type: WidthType.DXA }, margins: { top: 50, bottom: 50, left: 120, right: 120 },
          shading: i % 2 ? { type: ShadingType.CLEAR, fill: GREY } : undefined,
          children: [new Paragraph({ children: [T(s, { size: 20, color: "7F6000", bold: true })] })],
        }),
      ] })),
    ],
  });
}

// meta table: [key, value][] — light-blue label column
function metaTable(rows) {
  const col = [2400, CONTENT_W - 2400];
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: col,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 8, color: NAVY },
      bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: rows.map(([k, v]) => new TableRow({ children: [
      new TableCell({ width: { size: col[0], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        shading: { type: ShadingType.CLEAR, fill: LIGHT },
        children: [new Paragraph({ children: [B(k, { size: 20 })] })] }),
      new TableCell({ width: { size: col[1], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [T(v, { size: 20 })] })] }),
    ] })),
  });
}

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 },
    children: [B("NOTES DISKUSI BLUEPRINT", { size: 36, color: NAVY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 320 },
    children: [T("Project — subtitle", { size: 22, color: ACCENT })] }),
  metaTable([["Tanggal", "..."], ["Topik", "..."], ["Peserta", "..."]]),
  spacer(240),
  // heading("SESI 1 — ..."), heading("1.1 ...", HeadingLevel.HEADING_2),
  // bullet(...), labelBullet("Label: ", "rest"),
  // callout("decision", "KESIMPULAN / KEBIJAKAN", [...]), spacer(),
  // callout("open", "PERTANYAAN TERBUKA", [...]), spacer(),
  // heading("ACTION ITEMS"), actionTable([["action 1", "Open"], ...]),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { bold: true, color: NAVY, size: 28, font: "Calibri" },
        paragraph: { spacing: { before: 320, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { bold: true, color: ACCENT, size: 24, font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children,
  }],
});

const OUT = process.argv[2] || "notes.docx";
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("OK " + OUT); });
