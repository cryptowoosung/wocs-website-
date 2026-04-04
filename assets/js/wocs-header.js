/* ═══════════════════════════════════════════════════
   WOCS Header Component — Auto-injected on all pages
   Includes: Top bar, Logo, Navigation, Mega Menu, Language Selector
   ═══════════════════════════════════════════════════ */


// Flag country codes for flagcdn.com images (Windows doesn't render flag emojis!)
var LANG_CC = {ko:'kr',en:'us',ja:'jp',zh:'cn',es:'es',fr:'fr',de:'de',pt:'pt',it:'it',ar:'sa',ru:'ru',tr:'tr',tw:'tw',id:'id',th:'th'};
var currentCC = LANG_CC[typeof WOCS_LANG !== 'undefined' ? WOCS_LANG : 'ko'] || 'kr';
var flagImg = 'https://flagcdn.com/w40/' + currentCC + '.png';

function buildWocsHeader() {
  const nav = [
    { key: 'navProducts', href: '/products/index.html', mega: [
      { titleKey: 'megaGeoDomes', titleHref: '/products/geodesic-domes.html', links: [
        { key: 'megaCustomDomes', href: '/products/geodesic-domes-custom.html' },
        { key: 'megaPreconfigured', href: '/products/geodesic-domes-preconfigured.html' },
        { key: 'megaReadyShip', href: '/products/geodesic-domes-ready.html' },
      ]},
      { titleKey: 'megaSafariTents', titleHref: '/products/safari-tents.html', links: [
        { key: 'megaBasic', href: '/products/safari-basic.html' },
        { key: 'megaExtreme', href: '/products/safari-extreme.html' },
        { key: 'megaCabin', href: '/products/safari-cabin.html' },
        { key: 'megaElite', href: '/products/safari-elite.html' },
        { key: 'megaLuxury', href: '/products/safari-luxury.html' },
      ]},
      { titleKey: 'megaLuxuryTents', titleHref: '/products/luxury-tents.html', links: [
        { key: 'megaSignature_O', href: '/products/cocoon-house.html' },
        { key: 'megaSignature_A', href: '/products/sailing-tent.html' },
        { key: 'megaSignature_P', href: '/products/birdcage.html' },
        { key: 'megaPeakLodge', href: '/products/peak-lodge.html' },
        { key: 'megaNordicTipi', href: '/products/nordic-tipi.html' },
        { key: 'megaCubeCabin', href: '/products/cube-cabin.html' },
        { key: 'megaBellTents', href: '/products/bell-tent.html' },
        { key: 'megaDomeTents', href: '/products/dome-tent.html' },
      ]},
      { titleKey: 'megaAccessories', titleHref: '/products/modular-systems.html', links: [
        { key: 'megaModUnits', href: '/products/modular-units.html' },
        { key: 'megaModBath', href: '/products/modular-bath.html' },
        { key: 'megaModDeck', href: '/products/modular-deck.html' },
        { key: 'megaSolar', href: '/products/solar-system.html' },
        { key: 'megaAddons', href: '/products/addons.html' },
      ]},
    ]},
    { key: 'navOccasions', href: '/occasions/index.html', mega: [
      { titleKey: null, links: [
        { key: 'megaAirbnb', href: '/occasions/airbnb.html' },
        { key: 'megaResort', href: '/occasions/resort.html' },
        { key: 'megaWedding', href: '/occasions/wedding.html' },
        { key: 'megaHotel', href: '/occasions/hotel.html' },
        { key: 'megaHunting', href: '/occasions/glamping.html' },
        { key: 'megaGlampPod', href: '/occasions/glamping-pod.html' },
        { key: 'megaLuxCamp', href: '/occasions/glamping.html' },
        { key: 'megaPermanent', href: '/occasions/permanent.html' },
        { key: 'megaSports', href: '/occasions/sports.html' },
        { key: 'megaWinterCamp', href: '/occasions/winter.html' },
      ]},
    ]},
    { key: 'navProject', href: '/project/index.html', mega: [
      { titleKey: 'megaPlanning', links: [
        { key: 'megaPlanCases', href: '/project/planning-cases.html' },
        { key: 'megaStartBiz', href: '/project/start-business.html' },
        { key: 'megaBuyLand', href: '/project/buying-land.html' },
      ]},
      { titleKey: 'megaPartnership', links: [
        { key: 'megaFinancing', href: '/project/financing.html' },
        { key: 'megaRevShare', href: '/project/revenue-sharing.html' },
        { key: 'megaMultiOrder', href: '/contact/index.html?type=bulk' },
        { key: 'megaROI', href: '/contact/roi-calculator.html' },
      ]},
    ]},
    { key: 'navResources', href: '/resources/index.html', mega: [
      { titleKey: null, links: [
        { key: 'megaFAQs', href: '/resources/faq.html' },
        { key: 'megaBlog', href: '/resources/blog.html' },
        { key: 'megaDownloads', href: '/resources/downloads.html' },
        { key: 'megaReviewsLink', href: '/resources/reviews.html' },
        { key: 'megaDealer', href: '/resources/dealer.html' },
        { key: 'megaTeam', href: '/about/team.html' },
      ]},
    ]},
    { key: 'navGallery', href: '/gallery/index.html' },
    { key: 'navPortfolio', href: '/portfolio/index.html' },
    { key: 'navAbout', href: '/about/index.html' },
    { key: 'navContact', href: '/contact/index.html' },
  ];

  const langParam = WOCS_LANG !== 'ko' ? `?lang=${WOCS_LANG}` : '';
  // Auto-detect base path from current page location
  var base = (function() {
    var scripts = document.querySelectorAll('script[src*="wocs-header"]');
    if (scripts.length > 0) {
      var src = scripts[0].getAttribute('src');
      return src.replace('assets/js/wocs-header.js', '');
    }
    // Fallback: detect from WOCS_BASE or default
    if (typeof WOCS_BASE !== 'undefined') return WOCS_BASE;
    return '';
  })();
  function href(path) {
    var clean = path.replace(/^\//, '');
    var b = base + clean;
    if (!langParam) return b;
    if (b.indexOf('#') >= 0) {
      var parts = b.split('#');
      return parts[0] + (parts[0].indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG + '#' + parts[1];
    }
    return b + (b.indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG;
  }

  let navHTML = '';
  nav.forEach(item => {
    const hasMega = item.mega && item.mega.length > 0;
    const isMul = hasMega && item.mega.length > 1;
    let megaHTML = '';
    if (hasMega) {
      let cols = '';
      item.mega.forEach(col => {
        let links = '';
        col.links.forEach(link => {
          links += `<a class="mega-link" href="${href(link.href)}">${(function(){
            var t=tc(link.key);
            var m=t.match(/^(S-[A-Za-z ]+(?:EX|LX)?)\s*\((.+)\)$/);
            if(m) return m[1]+'<span class="mega-sub">'+m[2]+'</span>';
            var s=t.match(/^(Signature-[A-Z])\s*\((.+)\)$/);
            if(s) return s[1]+'<span class="mega-sub">'+s[2]+'</span>';
            return t;
          })()}</a>`;
        });
        const title = col.titleKey ? (col.titleHref ? `<a class="mega-title" href="${href(col.titleHref)}" style="text-decoration:none;display:block">${tc(col.titleKey)}</a>` : `<div class="mega-title">${tc(col.titleKey)}</div>`) : '';
        cols += `<div>${title}${links}</div>`;
      });
      megaHTML = `<div class="mega-menu ${isMul ? 'multi' : ''}">${cols}</div>`;
    }
    navHTML += `
      <li class="nav-item">
        <a class="nav-link" href="${href(item.href)}">${tc(item.key)}${hasMega ? '<span class="nav-arrow">▾</span>' : ''}</a>
        ${megaHTML}
      </li>`;
  });

  const html = `
    <div class="header-bar">
      <span>✆ ${tc('phone')}</span>
      <span>${tc('email')}</span>
    </div>
    <div class="header-main">
      <a class="header-logo" href="${href('index.html')}">
        <div class="header-logo-icon"><span>W</span></div>
        <div>
          <div class="header-logo-text">WOCS</div>
          <div class="header-logo-sub">MODULAR STRUCTURES</div>
        </div>
      </a>
      <nav>
        <ul class="nav-list">
          ${navHTML}
          <li style="margin-left:20px">
            <a class="btn-gold btn-sm" href="${href('contact/index.html')}">${tc('getQuote')}</a>
          </li>
          <li style="margin-left:12px;position:relative" id="lang-selector">
            <button onclick="var dd=document.getElementById('lang-dropdown');if(dd)dd.style.display=dd.style.display==='grid'?'none':'grid';" style="width:42px;height:42px;border-radius:50%;border:1.5px solid rgba(240,235,224,0.27);background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .4s;position:relative" onmouseover="this.style.borderColor='#c9a96e'" onmouseout="this.style.borderColor='rgba(240,235,224,0.27)'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="rgba(240,235,224,0.73)" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.5" ry="10"/><path d="M2 12h20"/><path d="M4 7h16" opacity=".3"/><path d="M4 17h16" opacity=".3"/></svg>
              <img src="${flagImg}" alt="" style="position:absolute;bottom:-4px;right:-4px;width:16px;height:16px;border-radius:50%;object-fit:cover;filter:drop-shadow(0 1px 3px rgba(0,0,0,0.7))" onerror="this.style.display='none'">
            </button>
            <div id="lang-dropdown" style="display:none;position:absolute;top:100%;right:0;background:rgba(9,9,11,0.96);backdrop-filter:blur(20px);border:1px solid rgba(201,169,110,0.15);padding:20px;margin-top:8px;z-index:1001;grid-template-columns:repeat(5,1fr);gap:16px;min-width:320px">
              <div onclick="wocsSetLang('ko')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/kr.png" style="width:100%;height:100%;object-fit:cover" alt="KR" onerror="this.parentNode.innerHTML='KR'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">한국어</span>
              </div>
              <div onclick="wocsSetLang('en')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/us.png" style="width:100%;height:100%;object-fit:cover" alt="US" onerror="this.parentNode.innerHTML='US'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">English</span>
              </div>
              <div onclick="wocsSetLang('ja')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/jp.png" style="width:100%;height:100%;object-fit:cover" alt="JP" onerror="this.parentNode.innerHTML='JP'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">日本語</span>
              </div>
              <div onclick="wocsSetLang('zh')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/cn.png" style="width:100%;height:100%;object-fit:cover" alt="CN" onerror="this.parentNode.innerHTML='CN'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">中文</span>
              </div>
              <div onclick="wocsSetLang('es')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/es.png" style="width:100%;height:100%;object-fit:cover" alt="ES" onerror="this.parentNode.innerHTML='ES'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Español</span>
              </div>
              <div onclick="wocsSetLang('fr')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/fr.png" style="width:100%;height:100%;object-fit:cover" alt="FR" onerror="this.parentNode.innerHTML='FR'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Français</span>
              </div>
              <div onclick="wocsSetLang('de')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/de.png" style="width:100%;height:100%;object-fit:cover" alt="DE" onerror="this.parentNode.innerHTML='DE'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Deutsch</span>
              </div>
              <div onclick="wocsSetLang('pt')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/pt.png" style="width:100%;height:100%;object-fit:cover" alt="PT" onerror="this.parentNode.innerHTML='PT'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Português</span>
              </div>
              <div onclick="wocsSetLang('it')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/it.png" style="width:100%;height:100%;object-fit:cover" alt="IT" onerror="this.parentNode.innerHTML='IT'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Italiano</span>
              </div>
              <div onclick="wocsSetLang('ru')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/ru.png" style="width:100%;height:100%;object-fit:cover" alt="RU" onerror="this.parentNode.innerHTML='RU'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Русский</span>
              </div>
              <div onclick="wocsSetLang('ar')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/sa.png" style="width:100%;height:100%;object-fit:cover" alt="SA" onerror="this.parentNode.innerHTML='SA'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">العربية</span>
              </div>
              <div onclick="wocsSetLang('tr')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/tr.png" style="width:100%;height:100%;object-fit:cover" alt="TR" onerror="this.parentNode.innerHTML='TR'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Türkçe</span>
              </div>
              <div onclick="wocsSetLang('tw')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/tw.png" style="width:100%;height:100%;object-fit:cover" alt="TW" onerror="this.parentNode.innerHTML='TW'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">繁體中文</span>
              </div>
              <div onclick="wocsSetLang('id')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/id.png" style="width:100%;height:100%;object-fit:cover" alt="ID" onerror="this.parentNode.innerHTML='ID'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">Bahasa</span>
              </div>
              <div onclick="wocsSetLang('th')" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;transition:transform .2s" onmouseover="this.style.transform='scale(1.15)'" onmouseout="this.style.transform='scale(1)'">
                <div style="width:36px;height:36px;border-radius:50%;border:2px solid rgba(201,169,110,0.3);overflow:hidden;display:flex;align-items:center;justify-content:center;background:#111">
                  <img src="https://flagcdn.com/w80/th.png" style="width:100%;height:100%;object-fit:cover" alt="TH" onerror="this.parentNode.innerHTML='TH'">
                </div>
                <span style="font-family:var(--font-body);font-size:9px;color:rgba(240,235,224,0.65);letter-spacing:0.5px">ไทย</span>
              </div>
            </div>
          </li>
        </ul>
      </nav>
    </div>`;

  const header = document.getElementById('wocs-header');
  if (header) {
    header.innerHTML = html;
    header.style.transition = 'all .5s';
  }

  // Scroll effect
  window.addEventListener('scroll', () => {
    const header = document.getElementById('wocs-header');
    if (!header) return;
    if (window.scrollY > 80) {
      header.classList.add('header-scrolled');
    } else {
      header.classList.remove('header-scrolled');
    }
  }, { passive: true });
}

// Auto-init
document.addEventListener('DOMContentLoaded', buildWocsHeader);


// Close language dropdown on outside click
document.addEventListener('click', function(e) {
  var dd = document.getElementById('lang-dropdown');
  var sel = document.getElementById('lang-selector');
  if (dd && sel && !sel.contains(e.target)) dd.style.display = 'none';
});

// ── Mobile Menu (완전 독립 패널) ──
function initMobileMenu() {
  var header = document.getElementById('wocs-header');
  if (!header) return;
  var main = header.querySelector('.header-main');
  if (!main) return;

  // 네비게이션 데이터 추출
  var navItems = header.querySelectorAll('.nav-item');

  // 언어 버튼
  var langBtn = document.createElement('button');
  langBtn.setAttribute('style','display:none;background:none;border:1px solid rgba(201,169,110,0.3);color:#c9a96e;padding:6px 10px;cursor:pointer;border-radius:4px;margin-right:6px;font-size:20px;vertical-align:middle;');
  langBtn.innerHTML = '&#127760;';

  // 햄버거 버튼
  var hbtn = document.createElement('button');
  hbtn.setAttribute('style','display:none;background:none;border:1px solid rgba(201,169,110,0.3);color:#c9a96e;font-size:22px;padding:6px 12px;cursor:pointer;');
  hbtn.innerHTML = '&#9776;';

  main.appendChild(langBtn);
  main.appendChild(hbtn);

  // 모바일 전용 패널 생성
  var panel = document.createElement('div');
  panel.id = 'wocs-mob-panel';
  panel.setAttribute('style','display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:#0a0a0c;z-index:999999;overflow-y:auto;padding:20px;box-sizing:border-box;');

  // 닫기 버튼
  var closeBtn = document.createElement('button');
  closeBtn.setAttribute('style','position:absolute;top:16px;right:16px;background:none;border:1px solid rgba(201,169,110,0.3);color:#c9a96e;font-size:22px;padding:6px 12px;cursor:pointer;z-index:1000000;');
  closeBtn.innerHTML = '&#x2715;';
  panel.appendChild(closeBtn);

  // 메뉴 컨테이너
  var menuDiv = document.createElement('div');
  menuDiv.setAttribute('style','margin-top:60px;');

  // navItems에서 메뉴 구성
  navItems.forEach(function(item) {
    var link = item.querySelector('.nav-link');
    var mega = item.querySelector('.mega-menu');
    if (!link) return;

    var row = document.createElement('div');
    row.setAttribute('style','border-bottom:1px solid rgba(201,169,110,0.1);');

    if (mega) {
      // 서브메뉴 있는 항목
      var topBtn = document.createElement('button');
      topBtn.setAttribute('style','width:100%;text-align:left;background:none;border:none;color:#f0ebe0;font-size:16px;padding:16px 8px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;letter-spacing:1px;');
      topBtn.innerHTML = (link.childNodes[0] ? link.childNodes[0].textContent.trim() : link.textContent.trim()) + '<span style="color:#c9a96e;font-size:12px;transition:transform 0.3s;display:inline-block;">&#9660;</span>';

      var subDiv = document.createElement('div');
      subDiv.setAttribute('style','display:none;padding:0 8px 12px;');

      // mega-link들 복사
      var megaLinks = mega.querySelectorAll('a');
      megaLinks.forEach(function(ml) {
        var a = document.createElement('a');
        a.href = ml.href;
        a.textContent = ml.textContent.trim();
        a.setAttribute('style','display:block;color:rgba(240,235,224,0.65);font-size:13px;padding:8px 12px;text-decoration:none;border-left:2px solid rgba(201,169,110,0.2);margin-bottom:2px;');
        subDiv.appendChild(a);
      });

      var isOpen = false;
      topBtn.addEventListener('click', function() {
        isOpen = !isOpen;
        subDiv.style.display = isOpen ? 'block' : 'none';
        var arrow = topBtn.querySelector('span');
        if (arrow) arrow.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
      });

      row.appendChild(topBtn);
      row.appendChild(subDiv);
    } else {
      // 서브메뉴 없는 항목
      var a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.textContent.trim();
      a.setAttribute('style','display:block;color:#f0ebe0;font-size:16px;padding:16px 8px;text-decoration:none;letter-spacing:1px;');
      row.appendChild(a);
    }

    menuDiv.appendChild(row);
  });

  // 언어 선택 (모바일 패널 하단)
  var langDiv = document.createElement('div');
  langDiv.setAttribute('style','margin-top:24px;padding:16px 8px;');
  langDiv.innerHTML = '<div style="color:rgba(240,235,224,0.4);font-size:11px;letter-spacing:2px;margin-bottom:12px;">LANGUAGE</div>';
  var langs = [{c:'ko',n:'한국어'},{c:'en',n:'English'},{c:'ja',n:'日本語'},{c:'zh',n:'中文'},{c:'es',n:'Español'},{c:'fr',n:'Français'},{c:'de',n:'Deutsch'},{c:'pt',n:'Português'},{c:'it',n:'Italiano'},{c:'ru',n:'Русский'},{c:'ar',n:'العربية'},{c:'tr',n:'Türkçe'},{c:'tw',n:'繁體中文'},{c:'id',n:'Bahasa'},{c:'th',n:'ไทย'}];
  var lgrid = document.createElement('div');
  lgrid.setAttribute('style','display:grid;grid-template-columns:repeat(3,1fr);gap:8px;');
  langs.forEach(function(l) {
    var b = document.createElement('button');
    b.setAttribute('style','background:rgba(201,169,110,0.08);border:1px solid rgba(201,169,110,0.2);color:#c9a96e;padding:8px;cursor:pointer;border-radius:4px;font-size:12px;');
    b.textContent = l.n;
    b.addEventListener('click', function() { wocsSetLang(l.c); });
    lgrid.appendChild(b);
  });
  langDiv.appendChild(lgrid);
  menuDiv.appendChild(langDiv);

  panel.appendChild(menuDiv);
  document.body.appendChild(panel);

  // 언어 버튼 클릭 → 패널 열고 언어 섹션으로 스크롤
  langBtn.addEventListener('click', function() {
    panel.style.display = 'block';
    hbtn.style.display = 'none';
    setTimeout(function() { langDiv.scrollIntoView({behavior:'smooth'}); }, 100);
  });

  // 햄버거 클릭
  hbtn.addEventListener('click', function() {
    panel.style.display = 'block';
    hbtn.style.display = 'none';
  });

  // 닫기
  closeBtn.addEventListener('click', function() {
    panel.style.display = 'none';
    if (window.innerWidth <= 768) hbtn.style.display = 'block';
  });

  // 반응형
  function checkMobile() {
    var isMob = window.innerWidth <= 768;
    hbtn.style.display = isMob ? 'block' : 'none';
    langBtn.style.display = isMob ? 'block' : 'none';
    var navList = header.querySelector('.nav-list');
    if (navList) navList.style.display = isMob ? 'none' : 'flex';
    if (!isMob) panel.style.display = 'none';
  }

  checkMobile();
  window.addEventListener('resize', checkMobile);
}

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(initMobileMenu, 300);
});

// Language switch function — works on local file:// AND http://
function wocsSetLang(code) {
  try { localStorage.setItem('wocs-lang', code); } catch(e) {}
  var loc = window.location.href;
  // Remove existing lang param
  loc = loc.replace(/[?&]lang=[a-z]{2}/gi, '');
  // Clean up leftover ? or &
  loc = loc.replace(/\?&/, '?').replace(/\?$/, '');
  // Add new lang param
  var sep = loc.indexOf('?') >= 0 ? '&' : '?';
  // Handle hash
  var hash = '';
  if (loc.indexOf('#') >= 0) {
    var parts = loc.split('#');
    loc = parts[0];
    hash = '#' + parts[1];
  }
  window.location.href = loc + sep + 'lang=' + code + hash;
}
