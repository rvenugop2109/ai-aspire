const express = require('express');
const puppeteer = require('puppeteer');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const templatePath  = path.join(__dirname, 'templates', 'offer_letter.html');
const logoPath      = path.join(__dirname, 'public', 'assets', 'mellone_logo.png');
const signaturePath = path.join(__dirname, 'public', 'assets', 'founder_signature.png');

// ── Shared helpers ────────────────────────────────────────────────────────────

function fmt(dateStr) {
  if (!dateStr) return '';
  const [y, m, d] = dateStr.split('-');
  return `${d}/${m}/${y}`;
}

function asDataUri(filePath, mime) {
  if (!fs.existsSync(filePath)) return '';
  const buf = fs.readFileSync(filePath);
  return `data:${mime};base64,${buf.toString('base64')}`;
}

function buildHtml(body) {
  const {
    candidateName,
    jobTitle,
    department,
    reportingManagerName,
    reportingManagerDesignation,
    dateOfJoining,
    totalCTC,
    offerDate,
    acceptanceDeadline,
  } = body;

  const reportingManager = reportingManagerDesignation
    ? `${reportingManagerName}, ${reportingManagerDesignation}`
    : reportingManagerName || '';

  const logoDataUri = asDataUri(logoPath, 'image/png');
  const sigDataUri  = asDataUri(signaturePath, 'image/png');

  const signatureHtml = sigDataUri
    ? `<img src="${sigDataUri}" alt="Founder Signature" class="sig-image" />`
    : '<div class="sig-line"></div>';

  let html = fs.readFileSync(templatePath, 'utf8');

  return html
    .replace(/{{CANDIDATE_NAME}}/g,    candidateName || '')
    .replace(/{{JOB_TITLE}}/g,         jobTitle || '')
    .replace(/{{DEPARTMENT}}/g,        department || '')
    .replace(/{{REPORTING_MANAGER}}/g, reportingManager)
    .replace(/{{DATE_OF_JOINING}}/g,   fmt(dateOfJoining))
    .replace(/{{TOTAL_CTC}}/g,         totalCTC || '')
    .replace(/{{OFFER_DATE}}/g,        fmt(offerDate))
    .replace(/{{ACCEPTANCE_DEADLINE}}/g, fmt(acceptanceDeadline))
    .replace(/{{FOUNDER_SIGNATURE_HTML}}/g, signatureHtml)
    .replace(/{{MELLONE_LOGO_SRC}}/g,  logoDataUri);
}

function filenameDate(dateOfJoining) {
  if (!dateOfJoining) return '00000000';
  const [y, m, d] = dateOfJoining.split('-');
  return `${d}${m}${y}`;
}

// ── Routes ────────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => res.json({ ok: true }));

// Preview — returns rendered HTML for browser display
// Uses upload.none() to parse multipart form data (no file fields anymore)
app.post('/preview', upload.none(), (req, res) => {
  try {
    const html = buildHtml(req.body);
    res.set('Content-Type', 'text/html; charset=utf-8');
    res.send(html);
  } catch (err) {
    console.error('Preview error:', err);
    res.status(500).json({ error: 'Preview failed: ' + err.message });
  }
});

// Generate PDF
app.post('/generate-pdf', upload.none(), async (req, res) => {
  let browser;
  try {
    const html = buildHtml(req.body);

    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle2', timeout: 60000 });

    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '20mm', right: '12mm', bottom: '12mm', left: '12mm' },
      timeout: 60000,
    });

    await browser.close();
    browser = null;

    const safeName = (req.body.candidateName || 'Candidate').replace(/\s+/g, '_');
    const filename = `Offer_Letter_${safeName}_${filenameDate(req.body.dateOfJoining)}.pdf`;

    res.set({
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Length': pdfBuffer.length,
    });
    res.send(pdfBuffer);
  } catch (err) {
    if (browser) await browser.close().catch(() => {});
    console.error('PDF generation error:', err);
    res.status(500).json({ error: 'PDF generation failed: ' + err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Mellone Offer Letter Tool → http://localhost:${PORT}`);
});
