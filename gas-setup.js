/**
 * ══════════════════════════════════════════════════════════
 *  WOCS Lead Capture — Google Apps Script (GAS)
 *  이 코드를 Google Apps Script 에디터에 붙여넣으세요.
 * ══════════════════════════════════════════════════════════
 *
 *  설정 방법:
 *  1. Google Drive → 새로 만들기 → Google Apps Script
 *  2. 이 코드를 전체 복사하여 붙여넣기
 *  3. 배포 → 새 배포 → 웹 앱 선택
 *     - 실행 주체: 본인
 *     - 액세스: 누구나
 *  4. 배포 후 생성된 URL을 복사
 *  5. wocs-site/assets/js/wocs-leads.js 파일의 GAS_URL 변수에 붙여넣기
 *  6. 첫 실행 시 자동으로 "WOCS_Leads" 시트가 생성됩니다.
 */

// ── Google Apps Script Code (여기부터 GAS에 붙여넣기) ──

/*
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("WOCS_Leads");

    // 시트가 없으면 생성 + 헤더 추가
    if (!sheet) {
      sheet = ss.insertSheet("WOCS_Leads");
      sheet.appendRow([
        "접수시간", "폼 유형", "이름", "연락처", "이메일",
        "국가", "회사명", "시공 지역", "부지 면적",
        "예상 예산", "오픈 목표일", "희망 모델",
        "문의 유형", "수량", "설치 장소", "메시지"
      ]);
      sheet.getRange(1, 1, 1, 16).setFontWeight("bold");
    }

    // 새 행 추가
    sheet.appendRow([
      new Date().toLocaleString("ko-KR", {timeZone: "Asia/Seoul"}),
      data.formType || "",
      data.name || "",
      data.phone || "",
      data.email || "",
      data.country || "",
      data.company || "",
      data.region || "",
      data.area || "",
      data.budget || "",
      data.targetDate || "",
      Array.isArray(data.models) ? data.models.join(", ") : (data.models || ""),
      data.inquiryType || "",
      data.quantity || "",
      data.location || "",
      data.message || ""
    ]);

    // 이메일 알림 (선택사항 — 본인 이메일로 변경)
    // MailApp.sendEmail("info@wocs.kr", "새 리드: " + (data.name || "익명"), JSON.stringify(data, null, 2));

    return ContentService
      .createTextOutput(JSON.stringify({status: "ok"}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// GET 요청 처리 (테스트용)
function doGet(e) {
  return ContentService
    .createTextOutput("WOCS Lead Capture is active.")
    .setMimeType(ContentService.MimeType.TEXT);
}
*/
