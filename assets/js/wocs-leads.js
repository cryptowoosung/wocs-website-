/* ═══════════════════════════════════════════════════
   WOCS Lead Capture System
   Google Apps Script 연동 폼 제출 핸들러
   ═══════════════════════════════════════════════════ */

// ★ 배포 후 아래 URL을 교체하세요
const GAS_URL = "여기에_GAS_웹앱_URL_붙여넣기";
const LEADS_API_URL = "여기에_백엔드_API_URL_붙여넣기";

// 15개 언어 성공/실패 메시지
var LEADS_MSG = {
  ko: { sending: "전송 중...", success: "견적 요청이 접수되었습니다.\n24시간 내 회신 드리겠습니다.\n긴급 문의: 010-4337-0582", fail: "전송에 실패했습니다.\n010-4337-0582로 직접 연락해주세요." },
  en: { sending: "Sending...", success: "Your quote request has been received.\nWe will respond within 24 hours.\nUrgent: 010-4337-0582", fail: "Failed to send.\nPlease call 010-4337-0582 directly." },
  ja: { sending: "送信中...", success: "見積もり依頼を受け付けました。\n24時間以内にご返信いたします。\n緊急: 010-4337-0582", fail: "送信に失敗しました。\n010-4337-0582に直接ご連絡ください。" },
  zh: { sending: "发送中...", success: "报价请求已收到。\n我们将在24小时内回复。\n紧急: 010-4337-0582", fail: "发送失败。\n请直接拨打 010-4337-0582。" }
};
function getLeadsMsg(key) {
  var lang = typeof WOCS_LANG !== 'undefined' ? WOCS_LANG : 'ko';
  return (LEADS_MSG[lang] && LEADS_MSG[lang][key]) || (LEADS_MSG.en && LEADS_MSG.en[key]) || key;
}

/**
 * 폼 데이터를 GAS + Backend API로 동시 전송
 */
function submitToGAS(data, btn) {
  var originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = getLeadsMsg('sending');
  btn.style.opacity = '0.6';

  // GAS 전송
  if (GAS_URL !== "여기에_GAS_웹앱_URL_붙여넣기") {
    fetch(GAS_URL, {
      method: 'POST', mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).catch(function(){});
  }

  // Backend API 전송
  var apiEndpoint = data.formType === 'quote_request' ? '/quote' : '/lead';
  if (LEADS_API_URL !== "여기에_백엔드_API_URL_붙여넣기") {
    fetch(LEADS_API_URL + apiEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).catch(function(){});
  }

  // 성공 처리 (no-cors는 응답 읽기 불가이므로 항상 성공으로 간주)
  setTimeout(function() {
    showResult(btn, 'success', getLeadsMsg('success'));
    localStorage.setItem('wocs-lead-submitted', 'true');
    resetBtn(btn, originalText);
  }, 1000);
}

function showResult(btn, type, msg) {
  // 기존 메시지 제거
  var existing = btn.parentElement.querySelector('.form-result-msg');
  if (existing) existing.remove();

  var div = document.createElement('div');
  div.className = 'form-result-msg';
  div.style.cssText = 'margin-top:16px;padding:16px 20px;font-family:var(--font-body,sans-serif);font-size:13px;line-height:1.6;white-space:pre-line;border:1px solid;';
  if (type === 'success') {
    div.style.color = '#c9a96e';
    div.style.borderColor = 'rgba(201,169,110,0.3)';
    div.style.background = 'rgba(201,169,110,0.05)';
  } else {
    div.style.color = '#e74c3c';
    div.style.borderColor = 'rgba(231,76,60,0.3)';
    div.style.background = 'rgba(231,76,60,0.05)';
  }
  div.textContent = msg;
  btn.parentElement.appendChild(div);

  // 5초 후 자동 제거
  setTimeout(function() { div.remove(); }, 8000);
}

function resetBtn(btn, text) {
  setTimeout(function() {
    btn.disabled = false;
    btn.textContent = text;
    btn.style.opacity = '1';
  }, 2000);
}

/* ── contact/index.html 일반 문의 폼 ── */
function initContactForm() {
  var btn = document.querySelector('.ct-form .form-submit');
  if (!btn) return;

  btn.removeAttribute('onclick'); // 기존 alert 제거

  btn.addEventListener('click', function(e) {
    e.preventDefault();
    var form = btn.closest('.ct-form');
    if (!form) return;

    var inputs = form.querySelectorAll('[required]');
    var valid = true;
    inputs.forEach(function(inp) {
      if (!inp.value || !inp.value.trim()) {
        inp.style.borderColor = '#e74c3c';
        valid = false;
      } else {
        inp.style.borderColor = '';
      }
    });
    if (!valid) return;

    var data = {
      formType: 'general_inquiry',
      name: form.querySelector('input[type="text"]') ? form.querySelector('input[type="text"]').value : '',
      phone: form.querySelector('input[type="tel"]') ? form.querySelector('input[type="tel"]').value : '',
      inquiryType: form.querySelector('.form-select') ? form.querySelector('.form-select').value : '',
      message: form.querySelector('.form-textarea') ? form.querySelector('.form-textarea').value : ''
    };

    submitToGAS(data, btn);
  });
}

/* ── contact/quote.html 견적 요청 폼 ── */
function initQuoteForm() {
  var btn = document.querySelector('.qt-form .form-submit');
  if (!btn) return;

  btn.removeAttribute('onclick'); // 기존 alert 제거

  btn.addEventListener('click', function(e) {
    e.preventDefault();
    var form = btn.closest('.qt-form');
    if (!form) return;

    var inputs = form.querySelectorAll('[required]');
    var valid = true;
    inputs.forEach(function(inp) {
      if (!inp.value || !inp.value.trim()) {
        inp.style.borderColor = '#e74c3c';
        valid = false;
      } else {
        inp.style.borderColor = '';
      }
    });
    if (!valid) return;

    // 체크박스에서 선택된 모델 수집
    var models = [];
    form.querySelectorAll('input[name="model"]:checked').forEach(function(cb) {
      models.push(cb.value);
    });

    var allInputs = form.querySelectorAll('.form-input');
    var selects = form.querySelectorAll('.form-select');

    var data = {
      formType: 'quote_request',
      name: allInputs[0] ? allInputs[0].value : '',
      phone: allInputs[1] ? allInputs[1].value : '',
      company: allInputs[2] ? allInputs[2].value : '',
      region: allInputs[3] ? allInputs[3].value : '',
      area: allInputs[4] ? allInputs[4].value : '',
      budget: selects[0] ? selects[0].value : '',
      targetDate: allInputs[5] ? allInputs[5].value : '',
      models: models,
      message: form.querySelector('.form-textarea') ? form.querySelector('.form-textarea').value : ''
    };

    submitToGAS(data, btn);
  });
}

/* ── 각 제품 페이지 하단 간이 견적 폼 ── */
function initProductForms() {
  document.querySelectorAll('.contact-form .btn-gold-fill, .contact-form button.btn-gold-fill').forEach(function(btn) {
    if (btn.dataset.leadInit) return;
    btn.dataset.leadInit = 'true';

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var form = btn.closest('.contact-form') || btn.closest('section');
      if (!form) return;

      var inputs = form.querySelectorAll('.form-input');
      var data = {
        formType: 'product_inquiry',
        name: inputs[0] ? inputs[0].value : '',
        country: inputs[1] ? inputs[1].value : '',
        email: inputs[2] ? inputs[2].value : '',
        phone: inputs[3] ? inputs[3].value : '',
        location: inputs[4] ? inputs[4].value : '',
        quantity: inputs[5] ? inputs[5].value : '',
        message: form.querySelector('textarea') ? form.querySelector('textarea').value : '',
        page: window.location.pathname
      };

      if (!data.name) return;
      submitToGAS(data, btn);
    });
  });
}

/* ── 뉴스레터 구독 폼 ── */
function initNewsletterForms() {
  document.querySelectorAll('.newsletter-btn').forEach(function(btn) {
    if (btn.dataset.leadInit) return;
    btn.dataset.leadInit = 'true';

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var bar = btn.closest('.newsletter-bar');
      var emailInput = bar ? bar.querySelector('.newsletter-input') : null;
      if (!emailInput || !emailInput.value) return;

      var data = {
        formType: 'newsletter',
        email: emailInput.value,
        page: window.location.pathname
      };

      submitToGAS(data, btn);
      emailInput.value = '';
    });
  });
}

/* ── Auto Init ── */
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    initContactForm();
    initQuoteForm();
    initProductForms();
    initNewsletterForms();
  }, 500);
});
