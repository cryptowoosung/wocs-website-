/**
 * ══════════════════════════════════════════════════════════
 *  WOCS Lead Capture — Google Apps Script
 *  이 코드를 Google Apps Script 에디터에 붙여넣으세요.
 * ══════════════════════════════════════════════════════════
 *
 *  설정 방법:
 *  1. Google Drive → 새로 만들기 → Google Apps Script
 *  2. 이 코드를 전체 복사하여 붙여넣기
 *  3. 스프레드시트 연결: 새 Google Sheets 만들고 ID 복사
 *  4. 배포 → 새 배포 → 웹 앱 선택
 *     - 실행 주체: 본인
 *     - 액세스: 누구나
 *  5. 배포 후 생성된 URL을 복사
 *  6. wocs-lead-popup.js의 POPUP_GAS_URL에 붙여넣기
 *
 *  스프레드시트 헤더 (첫 행에 수동 입력):
 *  접수시간 | 성함 | 연락처 | 시공지역 | 관심제품 | 유입페이지 | 언어 | 소스
 */

/*
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("리드DB");

    // 시트가 없으면 생성 + 헤더 추가
    if (!sheet) {
      sheet = ss.insertSheet("리드DB");
      sheet.appendRow([
        "접수시간", "성함", "연락처", "시공지역",
        "관심제품", "유입페이지", "언어", "소스"
      ]);
      sheet.getRange(1, 1, 1, 8).setFontWeight("bold");
    }

    // 새 행 추가
    sheet.appendRow([
      new Date().toLocaleString("ko-KR", {timeZone: "Asia/Seoul"}),
      data.name || "",
      data.phone || "",
      data.location || "",
      data.product || "",
      data.page || "",
      data.lang || "ko",
      data.source || "popup"
    ]);

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
    .createTextOutput("WOCS Lead Capture is active.")
    .setMimeType(ContentService.MimeType.TEXT);
}
*/
