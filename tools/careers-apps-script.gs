/**
 * Halawi & Partners: careers form receiver (Google Apps Script web app).
 * Bound to the spreadsheet "Halawi & Partners - Job applications".
 * Each application from https://halawipartners.com/careers/ becomes one row,
 * and the CV and work samples are saved in the Drive folder below.
 * Deploy: Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.
 * Daily summary: run installDigest() once; dailyDigest() then emails DIGEST_TO at 9:00 Cairo time
 * on days with new applications.
 */
var SHEET_ID = '1Sz3RERZSBtjDyEOEyVtHVBdupPsO-yEdVNmDCvecJZ8';
var SHEET_NAME = 'Applications';
var FOLDER_NAME = 'Halawi & Partners - CVs';
var HEADERS = ['Date', 'Name', 'Email', 'Phone', 'Location', 'Discipline', 'Experience', 'US codes', 'LinkedIn', 'Message', 'CV', 'Work samples', 'Status', 'Notes'];
var MAX_BYTES = 10 * 1024 * 1024;
var ALLOWED = /\.(pdf|doc|docx|jpg|jpeg|png)$/i;
var DIGEST_TO = 'shehab@halawipartners.com';
var DIGEST_MAX_ROWS = 25;

function doGet() {
  return json_({ ok: true, service: 'careers' });
}

function doPost(e) {
  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (err) {
    return json_({ ok: false, error: 'Bad request' });
  }
  if (data._gotcha) return json_({ ok: true });
  if (!data.name || !data.email || !data.cv || !data.cv.data) return json_({ ok: false, error: 'Missing fields' });
  var lock = LockService.getScriptLock();
  try {
    var folder = folder_();
    var stamp = Utilities.formatDate(new Date(), 'Africa/Cairo', 'yyyy-MM-dd HHmm');
    var who = String(data.name).replace(/[^\w\- ]+/g, '').trim().slice(0, 60) || 'Applicant';
    var cv = save_(folder, data.cv, stamp + ' ' + who + ' - CV');
    var samples = data.samples && data.samples.data ? save_(folder, data.samples, stamp + ' ' + who + ' - work samples') : '';
    lock.waitLock(30000);
    var sheet = sheet_();
    sheet.appendRow([
      new Date(),
      clean_(data.name), clean_(data.email), clean_(data.phone), clean_(data.location),
      clean_(data.field), clean_(data.experience), clean_(data.us), clean_(data.linkedin), clean_(data.message),
      '=HYPERLINK("' + cv + '","Open CV")',
      samples ? '=HYPERLINK("' + samples + '","Open samples")' : '',
      'New', ''
    ]);
    SpreadsheetApp.flush();
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
}

function save_(folder, f, label) {
  var name = String(f.name || 'file');
  var m = name.match(ALLOWED);
  if (!m) throw new Error('File type not allowed: ' + name);
  var bytes = Utilities.base64Decode(f.data);
  if (bytes.length > MAX_BYTES) throw new Error('File too large');
  var blob = Utilities.newBlob(bytes, f.type || 'application/octet-stream', label + m[0].toLowerCase());
  return folder.createFile(blob).getUrl();
}

function sheet_() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.getSheets()[0];
    sh.setName(SHEET_NAME);
  }
  if (sh.getLastRow() === 0) {
    sh.appendRow(HEADERS);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#0A1F3D').setFontColor('#FFFFFF');
    sh.setFrozenRows(1);
    sh.getRange('A:A').setNumberFormat('yyyy-mm-dd hh:mm');
  }
  return sh;
}

function folder_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('FOLDER_ID');
  if (id) {
    try { return DriveApp.getFolderById(id); } catch (ignore) {}
  }
  var it = DriveApp.getFoldersByName(FOLDER_NAME);
  var folder = it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER_NAME);
  props.setProperty('FOLDER_ID', folder.getId());
  return folder;
}

function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 2000);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor to create the header row and the CV folder, and to grant access. */
function setup() {
  sheet_();
  folder_();
}

/** One email a day (9:00 Cairo) listing the applications received since the last summary. */
function dailyDigest() {
  var props = PropertiesService.getScriptProperties();
  var since = new Date(Number(props.getProperty('LAST_DIGEST') || 0));
  var sh = sheet_();
  var last = sh.getLastRow();
  props.setProperty('LAST_DIGEST', String(Date.now()));
  if (last < 2) return;
  var rows = sh.getRange(2, 1, last - 1, 11).getValues();
  var links = sh.getRange(2, 11, last - 1, 1).getFormulas();
  var fresh = [];
  rows.forEach(function (r, i) {
    if (r[0] instanceof Date && r[0] > since) {
      var m = String(links[i][0]).match(/HYPERLINK\("([^"]+)"/);
      fresh.push({ r: r, cv: m ? m[1] : '' });
    }
  });
  if (!fresh.length) return;
  var esc = function (v) {
    return String(v).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  };
  var shown = fresh.slice(0, DIGEST_MAX_ROWS).map(function (x) {
    var r = x.r;
    var meta = [r[5], r[6], r[4]].filter(String).map(esc).join(' &middot; ');
    return '<tr><td style="padding:10px;border-bottom:1px solid #D5DDE7"><b>' + esc(r[1]) + '</b><br>' +
      '<span style="color:#53637A">' + meta + '</span></td>' +
      '<td style="padding:10px;border-bottom:1px solid #D5DDE7;text-align:right">' +
      (x.cv ? '<a href="' + x.cv + '" style="color:#A44F16">CV</a>' : '') + '</td></tr>';
  }).join('');
  var more = fresh.length > DIGEST_MAX_ROWS ? '<p style="color:#53637A">And ' + (fresh.length - DIGEST_MAX_ROWS) + ' more in the sheet.</p>' : '';
  var n = fresh.length;
  var subject = n + (n === 1 ? ' new job application' : ' new job applications') + ' - Halawi & Partners';
  var url = SpreadsheetApp.openById(SHEET_ID).getUrl();
  var html = '<div style="font-family:Arial,Helvetica,sans-serif;color:#0A1F3D;max-width:620px">' +
    '<h2 style="margin:0 0 6px">' + subject + '</h2>' +
    '<p style="margin:0 0 16px;color:#53637A">Received from the Careers page since the last summary.</p>' +
    '<table style="border-collapse:collapse;width:100%">' + shown + '</table>' + more +
    '<p style="margin:22px 0"><a href="' + url + '" style="background:#E8823E;color:#1B1206;padding:11px 18px;text-decoration:none;border-radius:4px;font-weight:bold">Open the applications sheet</a></p></div>';
  MailApp.sendEmail({ to: DIGEST_TO, subject: subject, htmlBody: html, name: 'Halawi & Partners website' });
}

/** Run once from the editor: schedules dailyDigest every day at 9:00 Cairo time. */
function installDigest() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'dailyDigest') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('dailyDigest').timeBased().atHour(9).everyDays(1).inTimezone('Africa/Cairo').create();
  PropertiesService.getScriptProperties().setProperty('LAST_DIGEST', String(Date.now()));
}
