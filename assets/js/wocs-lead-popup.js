/* ═══════════════════════════════════════════════════
   WOCS Lead Magnet Popup System
   - 15초 후 또는 스크롤 50% 시 팝업
   - 세션 쿨다운 (브라우저 닫으면 리셋)
   - 제출 완료 시 영구 차단 (localStorage)
   - GAS + Backend 동시 전송
   - 15개 언어 지원
   ═══════════════════════════════════════════════════ */

// ★ 배포 후 아래 URL을 교체하세요
const POPUP_GAS_URL = "https://script.google.com/macros/s/AKfycby7cq4Krqif_h0A059Rz4ip0KOJb3uJv8XU8fdHZRknNW-Zsmlsz8C2DQ_oQ2eHideE/exec";

// ── 15개 언어 번역 ──
const POPUP_TR = {
  ko: { headline: "프리미엄 글램핑 구조물 카탈로그", sub: "연락처를 남겨주시면 카탈로그 다운로드 링크를 즉시 보내드립니다.", privacy: "입력하신 정보는 카탈로그 발송 목적으로만 사용됩니다.", hide24h: "24시간 동안 팝업 끄기", namePh: "홍길동", phonePh: "010-0000-0000", locationPh: "예: 강원도 평창", productLabel: "관심 제품", optAll: "전체", optS: "S-시리즈", optD: "D-시리즈 돔", optSig: "Signature 시리즈", optMod: "모듈러 시스템", btn: "카탈로그 링크 받기", sending: "전송 중...", successTitle: "요청이 완료되었습니다!", successMsg: "곧 메시지로 카탈로그 링크가 발송됩니다.", successLink: "지금 바로 다운로드 →", failMsg: "전송에 실패했습니다. 010-4337-0582로 직접 연락해주세요.", nameLabel: "성함 *", phoneLabel: "연락처 *", locationLabel: "시공 예정 지역" },
  en: { hide24h: "Hide popup for 24 hours", headline: "Premium Glamping Structure Catalog", sub: "Leave your contact info and we'll send you the catalog download link instantly.", privacy: "Your information is used solely for catalog delivery purposes.", namePh: "John Doe", phonePh: "+82-10-0000-0000", locationPh: "e.g., Gangwon-do", productLabel: "Product Interest", optAll: "All Products", optS: "S-Series", optD: "D-Series Domes", optSig: "Signature Series", optMod: "Modular Systems", btn: "Get Catalog Link", sending: "Sending...", successTitle: "Request Complete!", successMsg: "A catalog link will be sent to you shortly.", successLink: "Download Now →", failMsg: "Failed to send. Please call 010-4337-0582 directly.", nameLabel: "Name *", phoneLabel: "Phone *", locationLabel: "Project Location" },
  ja: { hide24h: "24時間ポップアップを非表示", headline: "プレミアムグランピング構造物カタログ", sub: "連絡先をお残しいただければ、カタログダウンロードリンクを即時お送りします。", privacy: "ご入力いただいた情報はカタログ送付目的のみに使用されます。", namePh: "山田太郎", phonePh: "090-0000-0000", locationPh: "例：東京都", productLabel: "関心製品", optAll: "すべて", optS: "S-シリーズ", optD: "D-シリーズドーム", optSig: "Signatureシリーズ", optMod: "モジュラーシステム", btn: "カタログリンクを受け取る", sending: "送信中...", successTitle: "リクエスト完了！", successMsg: "まもなくカタログリンクが送信されます。", successLink: "今すぐダウンロード →", failMsg: "送信に失敗しました。010-4337-0582に直接ご連絡ください。", nameLabel: "お名前 *", phoneLabel: "連絡先 *", locationLabel: "施工予定地域" },
  zh: { hide24h: "24小时内隐藏弹窗", headline: "高端露营建筑产品目录", sub: "留下联系方式，我们将立即发送产品目录下载链接。", privacy: "您的信息仅用于目录发送目的。", namePh: "张三", phonePh: "138-0000-0000", locationPh: "例：江原道", productLabel: "感兴趣的产品", optAll: "全部", optS: "S系列", optD: "D系列穹顶", optSig: "Signature系列", optMod: "模块化系统", btn: "获取目录链接", sending: "发送中...", successTitle: "请求完成！", successMsg: "目录链接将很快发送给您。", successLink: "立即下载 →", failMsg: "发送失败。请直接拨打 010-4337-0582。", nameLabel: "姓名 *", phoneLabel: "联系方式 *", locationLabel: "施工地区" },
  es: { hide24h: "Ocultar popup 24 horas", headline: "Catálogo de Estructuras Glamping Premium", sub: "Deje su información de contacto y le enviaremos el enlace del catálogo al instante.", privacy: "Su información se utiliza únicamente para el envío del catálogo.", namePh: "Juan Pérez", phonePh: "+82-10-0000-0000", locationPh: "Ej: Gangwon-do", productLabel: "Producto de interés", optAll: "Todos", optS: "Serie S", optD: "Domos Serie D", optSig: "Serie Signature", optMod: "Sistema Modular", btn: "Obtener enlace del catálogo", sending: "Enviando...", successTitle: "¡Solicitud completada!", successMsg: "Pronto recibirá el enlace del catálogo.", successLink: "Descargar ahora →", failMsg: "Error al enviar. Llame al 010-4337-0582.", nameLabel: "Nombre *", phoneLabel: "Teléfono *", locationLabel: "Ubicación del proyecto" },
  fr: { hide24h: "Masquer le popup 24h", headline: "Catalogue de Structures Glamping Premium", sub: "Laissez vos coordonnées et nous vous enverrons le lien du catalogue instantanément.", privacy: "Vos informations sont utilisées uniquement pour l'envoi du catalogue.", namePh: "Jean Dupont", phonePh: "+82-10-0000-0000", locationPh: "Ex: Gangwon-do", productLabel: "Produit d'intérêt", optAll: "Tous", optS: "Série S", optD: "Dômes Série D", optSig: "Série Signature", optMod: "Système Modulaire", btn: "Recevoir le lien du catalogue", sending: "Envoi...", successTitle: "Demande terminée !", successMsg: "Le lien du catalogue vous sera envoyé sous peu.", successLink: "Télécharger maintenant →", failMsg: "Échec de l'envoi. Appelez le 010-4337-0582.", nameLabel: "Nom *", phoneLabel: "Téléphone *", locationLabel: "Lieu du projet" },
  de: { hide24h: "Popup 24 Stunden ausblenden", headline: "Premium Glamping-Strukturen Katalog", sub: "Hinterlassen Sie Ihre Kontaktdaten und wir senden Ihnen sofort den Katalog-Link.", privacy: "Ihre Daten werden ausschließlich für den Katalogversand verwendet.", namePh: "Max Mustermann", phonePh: "+82-10-0000-0000", locationPh: "z.B. Gangwon-do", productLabel: "Produktinteresse", optAll: "Alle", optS: "S-Serie", optD: "D-Serie Kuppeln", optSig: "Signature Serie", optMod: "Modulares System", btn: "Katalog-Link erhalten", sending: "Wird gesendet...", successTitle: "Anfrage abgeschlossen!", successMsg: "Der Katalog-Link wird Ihnen in Kürze zugesendet.", successLink: "Jetzt herunterladen →", failMsg: "Senden fehlgeschlagen. Rufen Sie 010-4337-0582 an.", nameLabel: "Name *", phoneLabel: "Telefon *", locationLabel: "Projektstandort" },
  pt: { hide24h: "Ocultar popup por 24 horas", headline: "Catálogo de Estruturas Glamping Premium", sub: "Deixe seus dados e enviaremos o link do catálogo instantaneamente.", privacy: "Suas informações são usadas apenas para envio do catálogo.", namePh: "João Silva", phonePh: "+82-10-0000-0000", locationPh: "Ex: Gangwon-do", productLabel: "Produto de interesse", optAll: "Todos", optS: "Série S", optD: "Domos Série D", optSig: "Série Signature", optMod: "Sistema Modular", btn: "Receber link do catálogo", sending: "Enviando...", successTitle: "Solicitação concluída!", successMsg: "O link do catálogo será enviado em breve.", successLink: "Baixar agora →", failMsg: "Falha no envio. Ligue para 010-4337-0582.", nameLabel: "Nome *", phoneLabel: "Telefone *", locationLabel: "Local do projeto" },
  it: { hide24h: "Nascondi popup per 24 ore", headline: "Catalogo Strutture Glamping Premium", sub: "Lascia i tuoi dati e ti invieremo il link del catalogo istantaneamente.", privacy: "Le tue informazioni sono utilizzate esclusivamente per l'invio del catalogo.", namePh: "Mario Rossi", phonePh: "+82-10-0000-0000", locationPh: "Es: Gangwon-do", productLabel: "Prodotto di interesse", optAll: "Tutti", optS: "Serie S", optD: "Cupole Serie D", optSig: "Serie Signature", optMod: "Sistema Modulare", btn: "Ricevi link catalogo", sending: "Invio...", successTitle: "Richiesta completata!", successMsg: "Il link del catalogo ti sarà inviato a breve.", successLink: "Scarica ora →", failMsg: "Invio fallito. Chiama 010-4337-0582.", nameLabel: "Nome *", phoneLabel: "Telefono *", locationLabel: "Luogo del progetto" },
  ar: { hide24h: "إخفاء النافذة لمدة 24 ساعة", headline: "كتالوج هياكل الغلامبينغ الفاخرة", sub: "اترك معلومات الاتصال وسنرسل لك رابط تحميل الكتالوج فوراً.", privacy: "تُستخدم معلوماتك فقط لإرسال الكتالوج.", namePh: "محمد أحمد", phonePh: "+82-10-0000-0000", locationPh: "مثال: جانجوون-دو", productLabel: "المنتج المطلوب", optAll: "الكل", optS: "سلسلة S", optD: "قباب سلسلة D", optSig: "سلسلة Signature", optMod: "نظام معياري", btn: "الحصول على رابط الكتالوج", sending: "جارِ الإرسال...", successTitle: "تم الطلب!", successMsg: "سيتم إرسال رابط الكتالوج قريباً.", successLink: "تحميل الآن →", failMsg: "فشل الإرسال. اتصل بـ 010-4337-0582.", nameLabel: "* الاسم", phoneLabel: "* الهاتف", locationLabel: "موقع المشروع" },
  ru: { hide24h: "Скрыть на 24 часа", headline: "Каталог премиальных глэмпинг-конструкций", sub: "Оставьте контакты — мы мгновенно отправим ссылку на каталог.", privacy: "Ваши данные используются только для отправки каталога.", namePh: "Иван Иванов", phonePh: "+82-10-0000-0000", locationPh: "Напр.: Канвондо", productLabel: "Интересующий продукт", optAll: "Все", optS: "S-серия", optD: "D-серия купола", optSig: "Signature серия", optMod: "Модульная система", btn: "Получить ссылку на каталог", sending: "Отправка...", successTitle: "Запрос выполнен!", successMsg: "Ссылка на каталог будет отправлена в ближайшее время.", successLink: "Скачать сейчас →", failMsg: "Ошибка отправки. Позвоните 010-4337-0582.", nameLabel: "Имя *", phoneLabel: "Телефон *", locationLabel: "Место проекта" },
  tr: { hide24h: "24 saat popup gizle", headline: "Premium Glamping Yapı Kataloğu", sub: "İletişim bilgilerinizi bırakın, katalog indirme linkini anında gönderelim.", privacy: "Bilgileriniz yalnızca katalog gönderimi amacıyla kullanılır.", namePh: "Ahmet Yılmaz", phonePh: "+82-10-0000-0000", locationPh: "Örn: Gangwon-do", productLabel: "İlgi alanı", optAll: "Tümü", optS: "S Serisi", optD: "D Serisi Kubbe", optSig: "Signature Serisi", optMod: "Modüler Sistem", btn: "Katalog linkini al", sending: "Gönderiliyor...", successTitle: "Talep tamamlandı!", successMsg: "Katalog linki kısa süre içinde gönderilecektir.", successLink: "Şimdi indir →", failMsg: "Gönderilemedi. 010-4337-0582'yi arayın.", nameLabel: "İsim *", phoneLabel: "Telefon *", locationLabel: "Proje konumu" },
  tw: { hide24h: "24小時內隱藏彈窗", headline: "高端露營建築產品目錄", sub: "留下聯繫方式，我們將立即發送產品目錄下載連結。", privacy: "您的資訊僅用於目錄發送目的。", namePh: "王小明", phonePh: "0912-000-000", locationPh: "例：江原道", productLabel: "感興趣的產品", optAll: "全部", optS: "S系列", optD: "D系列穹頂", optSig: "Signature系列", optMod: "模組化系統", btn: "取得目錄連結", sending: "傳送中...", successTitle: "請求完成！", successMsg: "目錄連結將很快發送給您。", successLink: "立即下載 →", failMsg: "傳送失敗。請直接撥打 010-4337-0582。", nameLabel: "姓名 *", phoneLabel: "聯絡方式 *", locationLabel: "施工地區" },
  id: { hide24h: "Sembunyikan popup 24 jam", headline: "Katalog Struktur Glamping Premium", sub: "Tinggalkan kontak Anda dan kami akan mengirimkan tautan katalog secara instan.", privacy: "Informasi Anda hanya digunakan untuk pengiriman katalog.", namePh: "Budi Santoso", phonePh: "+82-10-0000-0000", locationPh: "Contoh: Gangwon-do", productLabel: "Produk yang diminati", optAll: "Semua", optS: "Seri S", optD: "Kubah Seri D", optSig: "Seri Signature", optMod: "Sistem Modular", btn: "Dapatkan tautan katalog", sending: "Mengirim...", successTitle: "Permintaan selesai!", successMsg: "Tautan katalog akan segera dikirimkan.", successLink: "Unduh sekarang →", failMsg: "Gagal mengirim. Hubungi 010-4337-0582.", nameLabel: "Nama *", phoneLabel: "Telepon *", locationLabel: "Lokasi proyek" },
  th: { hide24h: "ซ่อนป๊อปอัพ 24 ชั่วโมง", headline: "แคตตาล็อกโครงสร้างแกลมปิ้งพรีเมียม", sub: "ฝากข้อมูลติดต่อ แล้วเราจะส่งลิงก์ดาวน์โหลดแคตตาล็อกให้ทันที", privacy: "ข้อมูลของคุณใช้เพื่อการส่งแคตตาล็อกเท่านั้น", namePh: "สมชาย", phonePh: "081-000-0000", locationPh: "เช่น คังวอนโด", productLabel: "ผลิตภัณฑ์ที่สนใจ", optAll: "ทั้งหมด", optS: "ซีรีส์ S", optD: "โดมซีรีส์ D", optSig: "ซีรีส์ Signature", optMod: "ระบบโมดูลาร์", btn: "รับลิงก์แคตตาล็อก", sending: "กำลังส่ง...", successTitle: "คำขอเสร็จสมบูรณ์!", successMsg: "ลิงก์แคตตาล็อกจะถูกส่งให้คุณในเร็วๆ นี้", successLink: "ดาวน์โหลดตอนนี้ →", failMsg: "ส่งไม่สำเร็จ โทร 010-4337-0582", nameLabel: "ชื่อ *", phoneLabel: "โทรศัพท์ *", locationLabel: "สถานที่โครงการ" }
};

function getPopupLang() {
  try { return typeof WOCS_LANG !== 'undefined' ? WOCS_LANG : (typeof getWocsLang === 'function' ? getWocsLang() : 'ko'); }
  catch(e) { return 'ko'; }
}

function pt(key) {
  var lang = getPopupLang();
  return (POPUP_TR[lang] && POPUP_TR[lang][key]) || (POPUP_TR.en && POPUP_TR.en[key]) || key;
}

// ── 쿨다운 체크 ──
function shouldShowPopup() {
  if (localStorage.getItem('wocs-lead-submitted')) return false;
  var h24 = localStorage.getItem('wocs-popup-24h');
  if (h24 && (Date.now() - parseInt(h24)) < 24 * 60 * 60 * 1000) return false;
  return true;
}

// ── 팝업 생성 ──
function createPopup() {
  if (document.getElementById('wocs-lead-popup')) return;

  var base = (typeof WOCS_BASE !== 'undefined') ? WOCS_BASE : '';
  var dlLink = base + 'resources/downloads.html';

  var overlay = document.createElement('div');
  overlay.id = 'wocs-lead-popup';
  overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(9,9,11,0.92);z-index:10000;display:flex;align-items:center;justify-content:center;animation:popupFadeIn .4s ease';

  overlay.innerHTML = '<style>@keyframes popupFadeIn{from{opacity:0}to{opacity:1}}@keyframes popupSlideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}</style>' +
    '<div id="popup-box" style="background:#1a1a1c;border:1px solid rgba(201,169,110,0.15);padding:48px 40px;max-width:480px;width:90%;position:relative;animation:popupSlideUp .5s ease">' +
      '<button id="popup-close" style="position:absolute;top:16px;right:20px;background:none;border:none;color:rgba(240,235,224,0.5);font-size:24px;cursor:pointer;font-family:sans-serif">&times;</button>' +
      '<div style="text-align:center;margin-bottom:24px">' +
        '<div style="font-family:\'Lexend\',sans-serif;font-size:10px;letter-spacing:4px;color:#c9a96e;text-transform:uppercase;margin-bottom:12px">FREE CATALOG</div>' +
        '<h3 id="popup-headline" style="font-family:\'Cormorant Garamond\',serif;font-size:clamp(22px,3vw,28px);font-weight:400;color:#f0ebe0;line-height:1.3">' + pt('headline') + '</h3>' +
        '<p style="font-family:\'Lexend\',sans-serif;font-size:12px;color:rgba(240,235,224,0.55);margin-top:8px;line-height:1.6">' + pt('sub') + '</p>' +
      '</div>' +
      '<div id="popup-form">' +
        '<div style="margin-bottom:14px"><label style="font-family:\'Lexend\',sans-serif;font-size:10px;letter-spacing:1px;color:#c9a96e;display:block;margin-bottom:6px">' + pt('nameLabel') + '</label>' +
          '<input id="popup-name" type="text" placeholder="' + pt('namePh') + '" required style="width:100%;padding:12px 14px;background:rgba(240,235,224,0.04);border:1px solid rgba(201,169,110,0.12);color:#f0ebe0;font-family:\'Lexend\',sans-serif;font-size:13px;outline:none;box-sizing:border-box"></div>' +
        '<div style="margin-bottom:14px"><label style="font-family:\'Lexend\',sans-serif;font-size:10px;letter-spacing:1px;color:#c9a96e;display:block;margin-bottom:6px">' + pt('phoneLabel') + '</label>' +
          '<input id="popup-phone" type="tel" placeholder="' + pt('phonePh') + '" required style="width:100%;padding:12px 14px;background:rgba(240,235,224,0.04);border:1px solid rgba(201,169,110,0.12);color:#f0ebe0;font-family:\'Lexend\',sans-serif;font-size:13px;outline:none;box-sizing:border-box"></div>' +
        '<div style="margin-bottom:14px"><label style="font-family:\'Lexend\',sans-serif;font-size:10px;letter-spacing:1px;color:#c9a96e;display:block;margin-bottom:6px">' + pt('locationLabel') + '</label>' +
          '<input id="popup-location" type="text" placeholder="' + pt('locationPh') + '" style="width:100%;padding:12px 14px;background:rgba(240,235,224,0.04);border:1px solid rgba(201,169,110,0.12);color:#f0ebe0;font-family:\'Lexend\',sans-serif;font-size:13px;outline:none;box-sizing:border-box"></div>' +
        '<div style="margin-bottom:20px"><label style="font-family:\'Lexend\',sans-serif;font-size:10px;letter-spacing:1px;color:#c9a96e;display:block;margin-bottom:6px">' + pt('productLabel') + '</label>' +
          '<select id="popup-product" style="width:100%;padding:12px 14px;background:rgba(240,235,224,0.04);border:1px solid rgba(201,169,110,0.12);color:#f0ebe0;font-family:\'Lexend\',sans-serif;font-size:13px;outline:none;box-sizing:border-box;appearance:none">' +
            '<option value="all">' + pt('optAll') + '</option>' +
            '<option value="s-series">' + pt('optS') + '</option>' +
            '<option value="d-series">' + pt('optD') + '</option>' +
            '<option value="signature">' + pt('optSig') + '</option>' +
            '<option value="modular">' + pt('optMod') + '</option>' +
          '</select></div>' +
        '<button id="popup-submit" style="width:100%;padding:14px;background:#c9a96e;color:#09090b;font-family:\'Lexend\',sans-serif;font-size:12px;font-weight:600;letter-spacing:2px;text-transform:uppercase;border:none;cursor:pointer;transition:all .3s">' + pt('btn') + '</button>' +
        '<label style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:14px;cursor:pointer"><input type="checkbox" id="popup-24h-check" style="accent-color:#c9a96e;width:14px;height:14px"><span style="font-family:\'Lexend\',sans-serif;font-size:11px;color:rgba(240,235,224,0.45)">' + pt('hide24h') + '</span></label>' +
        '<p style="font-family:\'Lexend\',sans-serif;font-size:10px;color:rgba(240,235,224,0.3);text-align:center;margin-top:8px;line-height:1.5">' + pt('privacy') + '</p>' +
      '</div>' +
      '<div id="popup-success" style="display:none;text-align:center;padding:20px 0">' +
        '<div style="font-size:48px;margin-bottom:16px">✅</div>' +
        '<h3 style="font-family:\'Cormorant Garamond\',serif;font-size:24px;color:#f0ebe0;font-weight:400">' + pt('successTitle') + '</h3>' +
        '<p style="font-family:\'Lexend\',sans-serif;font-size:13px;color:rgba(240,235,224,0.6);margin-top:10px;line-height:1.6">' + pt('successMsg') + '</p>' +
        '<a href="' + dlLink + '" style="display:inline-block;margin-top:20px;padding:12px 32px;background:#c9a96e;color:#09090b;font-family:\'Lexend\',sans-serif;font-size:12px;font-weight:600;letter-spacing:2px;text-decoration:none;text-transform:uppercase">' + pt('successLink') + '</a>' +
      '</div>' +
    '</div>';

  document.body.appendChild(overlay);

  // Close handlers
  document.getElementById('popup-close').addEventListener('click', closePopup);
  overlay.addEventListener('click', function(e) { if (e.target === overlay) closePopup(); });

  // Submit handler
  document.getElementById('popup-submit').addEventListener('click', submitPopup);
}

function closePopup() {
  var el = document.getElementById('wocs-lead-popup');
  if (el) {
    var cb = document.getElementById('popup-24h-check');
    if (cb && cb.checked) { localStorage.setItem('wocs-popup-24h', Date.now().toString()); }
    el.remove();
  }
}

function submitPopup() {
  var name = document.getElementById('popup-name').value.trim();
  var phone = document.getElementById('popup-phone').value.trim();
  var location = document.getElementById('popup-location').value.trim();
  var product = document.getElementById('popup-product').value;
  var btn = document.getElementById('popup-submit');

  // Validation
  if (!name) { document.getElementById('popup-name').style.borderColor = '#e74c3c'; return; }
  if (!phone) { document.getElementById('popup-phone').style.borderColor = '#e74c3c'; return; }

  var data = {
    name: name,
    phone: phone,
    message: location + (product ? ' [' + product + ']' : ''),
    page: window.location.href
  };

  btn.disabled = true;
  btn.textContent = pt('sending');
  btn.style.opacity = '0.6';

  function showSuccess() {
    document.getElementById('popup-form').style.display = 'none';
    document.getElementById('popup-success').style.display = 'block';
    localStorage.setItem('wocs-lead-submitted', 'true');
    alert('문의가 접수되었습니다');
  }

  fetch(POPUP_GAS_URL, {
    method: 'POST',
    mode: 'no-cors',
    headers: { 'Content-Type': 'text/plain' },
    body: JSON.stringify(data)
  }).catch(function() {});

  showSuccess();
}

// ── 팝업 트리거 ──
// [2026-03-26] 팝업 자동 실행 비활성화 — 다시 켜려면 아래 주석 해제
var popupShown = false;

function triggerPopup() {
  if (popupShown || !shouldShowPopup()) return;
  popupShown = true;
  createPopup();
}

// // Timer: 15초 후
// setTimeout(function() { triggerPopup(); }, 15000);

// // Scroll: 50% 이상
// window.addEventListener('scroll', function() {
//   var scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
//   if (scrollPercent >= 50) triggerPopup();
// }, { passive: true });
