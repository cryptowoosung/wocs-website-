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
  // 존재하는 페이지 목록 (없는 페이지는 상위 카테고리로 리다이렉트)
  var existingPages = [
    'index.html','products/index.html','products/geodesic-domes.html','products/safari-tents.html','products/luxury-tents.html',
    'about/index.html','contact/index.html','gallery/index.html',
    'occasions/index.html','portfolio/index.html','project/index.html','resources/index.html'
  ];
  var fallbackMap = {
    'products/':'products/index.html','occasions/':'occasions/index.html','project/':'project/index.html',
    'resources/':'resources/index.html','about/':'about/index.html','contact/':'contact/index.html',
    'gallery/':'gallery/index.html','portfolio/':'portfolio/index.html','legal/':'index.html'
  };
  function href(path) {
    var clean = path.replace(/^\//, '');
    // 존재하지 않는 페이지는 상위 카테고리로 연결
    if (existingPages.indexOf(clean) < 0 && clean.indexOf('#') < 0) {
      for (var prefix in fallbackMap) {
        if (clean.indexOf(prefix) === 0) { clean = fallbackMap[prefix]; break; }
      }
    }
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
            <button onclick="document.getElementById('lang-dropdown').style.display=document.getElementById('lang-dropdown').style.display==='grid'?'none':'grid'" style="width:42px;height:42px;border-radius:50%;border:1.5px solid rgba(240,235,224,0.27);background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .4s;position:relative" onmouseover="this.style.borderColor='#c9a96e'" onmouseout="this.style.borderColor='rgba(240,235,224,0.27)'">
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

// Auto-init (handle both before and after DOMContentLoaded)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', buildWocsHeader);
} else {
  buildWocsHeader();
}


// Close language dropdown on outside click
document.addEventListener('click', function(e) {
  var dd = document.getElementById('lang-dropdown');
  var sel = document.getElementById('lang-selector');
  if (dd && sel && !sel.contains(e.target)) dd.style.display = 'none';
});

// ── Mobile Menu (Accordion + Language + Fullscreen Panel) ──

function initMobileMenu() {
  var header = document.getElementById('wocs-header');
  if (!header) return;
  var main = header.querySelector('.header-main');
  if (!main) return;
  var navList = header.querySelector('.nav-list');
  var navItems = header.querySelectorAll('.nav-item');

  // Inject mobile CSS
  var mobileCSS = document.createElement('style');
  mobileCSS.textContent = `
    #mobile-hamburger, #mobile-lang-btn { display:none; }
    @media(max-width:1024px) {
      .nav-list { display:none!important; }
      #mobile-hamburger { display:block!important; background:none; border:none; color:#c9a96e; font-size:28px; cursor:pointer; padding:8px; z-index:100000; }
      #mobile-lang-btn { display:flex!important; align-items:center; justify-content:center; width:38px; height:38px; border-radius:50%; border:1.5px solid rgba(201,169,110,0.3); background:transparent; cursor:pointer; z-index:100000; position:relative; }
      #mobile-lang-btn:active { border-color:#c9a96e; }
      .mob-controls { display:flex; align-items:center; gap:8px; }
    }
    #mob-panel { display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(9,9,11,0.97); z-index:99999; padding:80px 24px 40px; overflow-y:auto; }
    #mob-panel.open { display:block; animation:mobSlideDown .3s ease; }
    #mob-panel .mob-close { position:absolute; top:20px; right:20px; background:none; border:none; color:#c9a96e; font-size:28px; cursor:pointer; z-index:100000; }
    #mob-panel .mob-nav-item { display:flex; justify-content:space-between; align-items:center; padding:16px 0; border-bottom:1px solid rgba(201,169,110,0.12); font-family:'Lexend',sans-serif; font-size:16px; color:rgba(240,235,224,0.8); cursor:pointer; background:none; border-left:none; border-right:none; border-top:none; width:100%; text-align:left; text-decoration:none; }
    #mob-panel .mob-nav-item:active { color:#c9a96e; }
    #mob-panel .mob-arrow { font-size:12px; color:#c9a96e; transition:transform .3s; display:inline-block; }
    #mob-panel .mob-arrow.open { transform:rotate(180deg); }
    #mob-panel .mob-submenu { max-height:0; overflow:hidden; transition:max-height .35s ease; padding-left:16px; }
    #mob-panel .mob-submenu.open { max-height:2000px; }
    #mob-panel .mob-submenu .mega-title { display:block; padding:12px 0 4px; font-size:13px; color:#c9a96e; font-family:'Lexend',sans-serif; letter-spacing:1px; font-weight:600; text-decoration:none; }
    #mob-panel .mob-submenu .mega-link { display:block; padding:8px 0 8px 12px; font-size:14px; color:rgba(240,235,224,0.55); text-decoration:none; border-left:1px solid rgba(201,169,110,0.1); }
    #mob-panel .mob-submenu .mega-link:active { color:#c9a96e; }
    #mob-panel .mob-lang-bar { display:flex; align-items:center; gap:12px; padding:16px 0; border-bottom:1px solid rgba(201,169,110,0.12); }
    #mob-panel .mob-lang-toggle { display:flex; align-items:center; gap:6px; background:none; border:1.5px solid rgba(201,169,110,0.3); color:rgba(240,235,224,0.8); padding:8px 14px; cursor:pointer; font-family:'Lexend',sans-serif; font-size:13px; border-radius:4px; }
    #mob-panel .mob-lang-grid { display:none; grid-template-columns:1fr 1fr; gap:4px; padding:8px 0 16px; border-bottom:1px solid rgba(201,169,110,0.12); }
    #mob-panel .mob-lang-grid.open { display:grid; }
    #mob-panel .mob-lang-grid button { display:flex; align-items:center; gap:8px; padding:10px 12px; background:transparent; border:none; color:rgba(240,235,224,0.7); font-size:14px; cursor:pointer; font-family:'Lexend',sans-serif; text-align:left; border-radius:4px; }
    #mob-panel .mob-lang-grid button:active { background:rgba(201,169,110,0.15); }
    #mob-panel .mob-lang-grid button.active { background:rgba(201,169,110,0.15); color:#c9a96e; font-weight:600; }
    body.mob-open { overflow:hidden; }
    @keyframes mobSlideDown { from{opacity:0;transform:translateY(-20px)} to{opacity:1;transform:translateY(0)} }
  `;
  document.head.appendChild(mobileCSS);

  // Language data
  var langs = [
    {code:'ko',cc:'kr',name:'한국어'},{code:'en',cc:'us',name:'English'},{code:'ja',cc:'jp',name:'日本語'},
    {code:'zh',cc:'cn',name:'中文'},{code:'es',cc:'es',name:'Español'},{code:'fr',cc:'fr',name:'Français'},
    {code:'de',cc:'de',name:'Deutsch'},{code:'pt',cc:'pt',name:'Português'},{code:'it',cc:'it',name:'Italiano'},
    {code:'ar',cc:'sa',name:'العربية'},{code:'ru',cc:'ru',name:'Русский'},{code:'tr',cc:'tr',name:'Türkçe'},
    {code:'tw',cc:'tw',name:'繁體中文'},{code:'id',cc:'id',name:'Bahasa'},{code:'th',cc:'th',name:'ไทย'}
  ];
  var curLang = langs.find(function(l){return l.code===WOCS_LANG}) || langs[0];

  // Create mobile controls (lang icon + hamburger)
  var controls = document.createElement('div');
  controls.className = 'mob-controls';
  controls.innerHTML = '<button id="mobile-lang-btn">'
    + '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="rgba(240,235,224,0.73)" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.5" ry="10"/><path d="M2 12h20"/></svg>'
    + '<img src="https://flagcdn.com/w40/'+curLang.cc+'.png" alt="" style="position:absolute;bottom:-2px;right:-2px;width:14px;height:14px;border-radius:50%;object-fit:cover" onerror="this.style.display=\'none\'">'
    + '</button>'
    + '<button id="mobile-hamburger">☰</button>';
  main.appendChild(controls);

  // Build mobile panel HTML
  var panelHTML = '<button class="mob-close">✕</button>';

  // Language bar
  panelHTML += '<div class="mob-lang-bar"><button class="mob-lang-toggle" id="mob-lang-toggle">'
    + '<img src="https://flagcdn.com/w40/'+curLang.cc+'.png" style="width:20px;height:20px;border-radius:50%;object-fit:cover" onerror="this.style.display=\'none\'" alt="">'
    + ' '+curLang.name+' <span style="font-size:10px;margin-left:4px">▼</span></button></div>';
  panelHTML += '<div class="mob-lang-grid" id="mob-lang-grid">';
  langs.forEach(function(lang) {
    panelHTML += '<button class="'+(lang.code===WOCS_LANG?'active':'')+'" data-lang="'+lang.code+'">'
      + '<img src="https://flagcdn.com/w40/'+lang.cc+'.png" style="width:18px;height:18px;border-radius:50%;object-fit:cover" onerror="this.style.display=\'none\'" alt="'+lang.cc+'">'
      + ' '+lang.name+'</button>';
  });
  panelHTML += '</div>';

  // Nav items with accordion
  navItems.forEach(function(item, idx) {
    var link = item.querySelector('.nav-link');
    var mega = item.querySelector('.mega-menu');
    var label = link ? link.textContent.replace('▾','').trim() : '';
    var itemHref = link ? link.getAttribute('href') : '#';

    if (mega) {
      panelHTML += '<button class="mob-nav-item" data-accordion="'+idx+'">'+label+' <span class="mob-arrow" id="mob-arrow-'+idx+'">▼</span></button>';
      panelHTML += '<div class="mob-submenu" id="mob-sub-'+idx+'">'+mega.innerHTML+'</div>';
    } else {
      panelHTML += '<a class="mob-nav-item" href="'+itemHref+'">'+label+'</a>';
    }
  });

  // Create panel element on body
  var panel = document.createElement('div');
  panel.id = 'mob-panel';
  panel.innerHTML = panelHTML;
  document.body.appendChild(panel);

  // State
  var isOpen = false;
  var openAccordion = null;
  var langGridOpen = false;

  function openPanel() { panel.classList.add('open'); document.body.classList.add('mob-open'); isOpen = true; }
  function closePanel() { panel.classList.remove('open'); document.body.classList.remove('mob-open'); isOpen = false; openAccordion = null; langGridOpen = false; var grid = document.getElementById('mob-lang-grid'); if(grid) grid.classList.remove('open'); }

  // Hamburger
  var hamburger = document.getElementById('mobile-hamburger');
  function onHamburger(e) { e.preventDefault(); e.stopPropagation(); if(isOpen){closePanel();hamburger.innerHTML='☰';}else{openPanel();hamburger.innerHTML='✕';} }
  hamburger.addEventListener('click', onHamburger);
  hamburger.addEventListener('touchstart', function(e){e.preventDefault();onHamburger(e);}, {passive:false});

  // Lang icon opens panel with lang grid
  var langBtn = document.getElementById('mobile-lang-btn');
  function onLangBtn(e) { e.preventDefault(); e.stopPropagation(); openPanel(); hamburger.innerHTML='✕'; var grid=document.getElementById('mob-lang-grid'); if(grid){grid.classList.add('open');langGridOpen=true;} }
  langBtn.addEventListener('click', onLangBtn);
  langBtn.addEventListener('touchstart', function(e){e.preventDefault();onLangBtn(e);}, {passive:false});

  // Close button
  var closeBtn = panel.querySelector('.mob-close');
  function onClose(e) { e.preventDefault(); closePanel(); hamburger.innerHTML='☰'; }
  closeBtn.addEventListener('click', onClose);
  closeBtn.addEventListener('touchstart', function(e){e.preventDefault();onClose(e);}, {passive:false});

  // Lang toggle inside panel
  var langToggle = document.getElementById('mob-lang-toggle');
  if (langToggle) {
    function onLangToggle(e) { e.preventDefault(); e.stopPropagation(); var grid=document.getElementById('mob-lang-grid'); if(grid){langGridOpen=!langGridOpen; if(langGridOpen){grid.classList.add('open');}else{grid.classList.remove('open');}} }
    langToggle.addEventListener('click', onLangToggle);
    langToggle.addEventListener('touchstart', function(e){e.preventDefault();onLangToggle(e);}, {passive:false});
  }

  // Lang grid buttons
  var langBtns = panel.querySelectorAll('.mob-lang-grid button[data-lang]');
  langBtns.forEach(function(btn) {
    function onLang(e) { e.preventDefault(); wocsSetLang(btn.getAttribute('data-lang')); }
    btn.addEventListener('click', onLang);
    btn.addEventListener('touchstart', function(e){e.preventDefault();onLang(e);}, {passive:false});
  });

  // Accordion buttons
  var accBtns = panel.querySelectorAll('[data-accordion]');
  accBtns.forEach(function(btn) {
    function onAcc(e) {
      e.preventDefault(); e.stopPropagation();
      var idx = btn.getAttribute('data-accordion');
      var sub = document.getElementById('mob-sub-'+idx);
      var arrow = document.getElementById('mob-arrow-'+idx);

      if (openAccordion === idx) {
        // Close current
        if(sub) sub.classList.remove('open');
        if(arrow) arrow.classList.remove('open');
        openAccordion = null;
      } else {
        // Close previous
        if (openAccordion !== null) {
          var prevSub = document.getElementById('mob-sub-'+openAccordion);
          var prevArrow = document.getElementById('mob-arrow-'+openAccordion);
          if(prevSub) prevSub.classList.remove('open');
          if(prevArrow) prevArrow.classList.remove('open');
        }
        // Open new
        if(sub) sub.classList.add('open');
        if(arrow) arrow.classList.add('open');
        openAccordion = idx;

      }
    }
    btn.addEventListener('click', onAcc);
    btn.addEventListener('touchstart', function(e){e.preventDefault();onAcc(e);}, {passive:false});
  });

  // Close panel when submenu link clicked
  var subLinks = panel.querySelectorAll('.mega-link');
  subLinks.forEach(function(link) {
    link.addEventListener('click', function() { closePanel(); hamburger.innerHTML='☰'; });
  });

  // Desktop: show nav, hide controls
  function checkMobile() {
    if (window.innerWidth > 1024) {
      if (navList) navList.style.display = 'flex';
      closePanel(); hamburger.innerHTML = '☰';
    } else {
      if (navList) navList.style.display = 'none';
    }
  }
  checkMobile();
  window.addEventListener('resize', checkMobile);
}

// Init mobile menu (handle both before and after DOMContentLoaded)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initMobileMenu, 200);
  });
} else {
  setTimeout(initMobileMenu, 200);
}

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
