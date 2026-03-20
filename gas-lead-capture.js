/**
 * ══════════════════════════════════════════════════════════
 *  WOCS Lead Capture — Google Apps Script (통합)
 *  팝업 리드 + 견적 폼 + 일반 문의 모두 처리
 *  이 코드를 Google Apps Script 에디터에 붙여넣으세요.
 * ══════════════════════════════════════════════════════════
 *
 *  스프레드시트 시트 2개 필요:
 *  1) "리드DB" — 팝업/일반문의용
 *     헤더: 접수시간 | 소스 | 성함 | 연락처 | 이메일 | 시공지역 | 관심제품 | 유입페이지 | 언어
 *
 *  2) "견적요청" — quote 폼용
 *     헤더: 접수시간 | 이름 | 연락처 | 이메일 | 국가 | 회사 | 시공지역 | 면적 | 예산 | 오픈목표 | 모델 | 메시지 | 유입페이지
 */

/*
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var source = data.formType || data.source || "popup";

    if (source === "quote_request") {
      // ── 견적 요청 ──
      var sheet = ss.getSheetByName("견적요청");
      if (!sheet) {
        sheet = ss.insertSheet("견적요청");
        sheet.appendRow(["접수시간","이름","연락처","이메일","국가","회사","시공지역","면적","예산","오픈목표","모델","메시지","유입페이지"]);
        sheet.getRange(1,1,1,13).setFontWeight("bold");
      }
      var models = Array.isArray(data.models) ? data.models.join(", ") : (data.models || "");
      sheet.appendRow([
        new Date().toLocaleString("ko-KR", {timeZone: "Asia/Seoul"}),
        data.name || "", data.phone || "", data.email || "",
        data.country || "", data.company || "",
        data.region || data.location || "",
        data.area || "", data.budget || "", data.targetDate || "",
        models, data.message || "", data.page || ""
      ]);
    } else {
      // ── 팝업 리드 / 일반 문의 ──
      var sheet = ss.getSheetByName("리드DB");
      if (!sheet) {
        sheet = ss.insertSheet("리드DB");
        sheet.appendRow(["접수시간","소스","성함","연락처","이메일","시공지역","관심제품","문의유형","메시지","유입페이지","언어"]);
        sheet.getRange(1,1,1,11).setFontWeight("bold");
      }
      sheet.appendRow([
        new Date().toLocaleString("ko-KR", {timeZone: "Asia/Seoul"}),
        source,
        data.name || "", data.phone || "", data.email || "",
        data.location || "", data.product || "",
        data.inquiryType || "", data.message || "",
        data.page || "", data.lang || "ko"
      ]);
    }

    return ContentService
      .createTextOutput(JSON.stringify({status: "ok"}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput("WOCS Lead Capture is active. Supports: popup, quote_request, general_inquiry")
    .setMimeType(ContentService.MimeType.TEXT);
}
*/
