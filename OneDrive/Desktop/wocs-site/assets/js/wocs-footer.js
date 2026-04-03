/* ═══════════════════════════════════════════════════
   WOCS Footer + Common Utilities
   ═══════════════════════════════════════════════════ */

// ── Footer Component ──
function buildWocsFooter() {
  const langParam = WOCS_LANG !== 'ko' ? `?lang=${WOCS_LANG}` : '';
  var base = (function() {
    var scripts = document.querySelectorAll('script[src*="wocs-footer"]');
    if (scripts.length > 0) return scripts[0].getAttribute('src').replace('assets/js/wocs-footer.js', '');
    if (typeof WOCS_BASE !== 'undefined') return WOCS_BASE;
    return '';
  })();
  function href(p) {
    var clean = p.replace(/^\//, '');
    var b = base + clean;
    if (!langParam) return b;
    if (b.indexOf('#') >= 0) {
      var parts = b.split('#');
      return parts[0] + (parts[0].indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG + '#' + parts[1];
    }
    return b + (b.indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG;
  }

  const html = `
    <div class="footer-grid">
      <div class="footer-brand">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
          <div style="width:36px;height:36px;border:2px solid var(--gold);transform:rotate(45deg);display:flex;align-items:center;justify-content:center">
            <span style="transform:rotate(-45deg);font-weight:700;font-size:16px;color:var(--gold)">W</span>
          </div>
          <div>
            <div style="font-weight:600;font-size:18px;letter-spacing:4px;color:var(--ivory)">WOCS</div>
            <div class="font-body" style="font-size:7px;letter-spacing:3px;color:var(--gold)">MODULAR STRUCTURES</div>
          </div>
        </div>
        <p>${tc('footDesc')}</p>
        <div class="font-body" style="font-size:12px;color:rgba(240,235,224,0.53)">
          <div style="margin-bottom:6px">✆ ${tc('phone')}</div>
          <div>✉ ${tc('email')}</div>
        </div>
      </div>
      <div>
        <div class="footer-col-title">${tc('footProducts')}</div>
        <a class="footer-link" href="${href('/products/geodesic-domes.html')}">${tc('megaGeoDomes')}</a>
        <a class="footer-link" href="${href('/products/safari-tents.html')}">${tc('megaSafariTents')}</a>
        <a class="footer-link" href="${href('/products/luxury-tents.html')}">${tc('megaLuxuryTents')}</a>
        <a class="footer-link" href="${href('/products/modular-systems.html')}">${tc('megaAccessories')}</a>
        <a class="footer-link" href="${href('/products/universal-joint.html')}">${tc("fJoint")}</a>
      </div>
      <div>
        <div class="footer-col-title">${tc('footCompany')}</div>
        <a class="footer-link" href="${href('/about/index.html')}">${tc("fAbout")}</a>
        <a class="footer-link" href="${href('/about/technology.html')}">${tc("fTech")}</a>
        <a class="footer-link" href="${href('/about/showroom.html')}">${tc("fShowroom")}</a>
        <a class="footer-link" href="${href('/resources/blog.html')}">${tc("megaBlog")}</a>
        <a class="footer-link" href="${href('/resources/reviews.html')}">${tc("megaReviewsLink")}</a>
        <a class="footer-link" href="${href('/gallery/index.html')}">${tc("navGallery")}</a>
        <a class="footer-link" href="${href('/portfolio/index.html')}">${tc("navPortfolio")}</a>
        <a class="footer-link" href="${href('/resources/downloads.html')}">${tc("megaDownloads")}</a>
        <a class="footer-link" href="${href('/contact/index.html')}">${tc("navContact")}</a>
      </div>
      <div>
        <div class="footer-col-title">${tc('footPartners')}</div>
        <a class="footer-link" href="${href('/project/financing.html')}">${tc('megaFinancing')}</a>
        <a class="footer-link" href="${href('/project/revenue-sharing.html')}">${tc('megaRevShare')}</a>
        <a class="footer-link" href="${href('/contact/index.html')}">${tc("fBulk")}</a>
        <a class="footer-link" href="${href('/contact/roi-calculator.html')}">${tc("megaROI")}</a>
        <a class="footer-link" href="${href('/resources/dealer.html')}">${tc("megaDealer")}</a>
        <a class="footer-link" href="${href('/resources/downloads.html')}">${tc("fShipInfo")}</a>
        <a class="footer-link" href="${href('/resources/faq.html')}">FAQ</a>
      </div>
      <div>
        <div class="footer-col-title">${tc('footLegal')}</div>
        <a class="footer-link" href="${href('/legal/terms.html')}">${tc("fTerms")}</a>
        <a class="footer-link" href="${href('/legal/privacy.html')}">${tc("fPrivacy")}</a>
        <a class="footer-link" href="${href('/resources/downloads.html')}">${tc("fShipping")}</a>
        <a class="footer-link" href="${href('/legal/cookies.html')}">${tc("fCookie")}</a>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copy">${tc('footCopy')}
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px;margin-top:40px;padding-top:30px;border-top:1px solid rgba(201,169,110,0.12)">
        <div class="social-links">
          <a class="social-link" href="#" title="YouTube">▶</a>
          <a class="social-link" href="#" title="Instagram">📷</a>
          <a class="social-link" href="#" title="Facebook">f</a>
          <a class="social-link" href="#" title="Blog">B</a>
        </div>
        <div class="partner-logos"><span>ISO 9001</span><span>CE</span><span>SGS</span></div>
      </div></div>
    </div>`;

  const footer = document.getElementById('wocs-footer');
  if (footer) {
    footer.className = 'footer';
    footer.innerHTML = html;
  }
}

// ── CTA Section (reusable) ──
function buildWocsCTA(targetId) {
  const el = document.getElementById(targetId || 'wocs-cta');
  if (!el) return;
  const langParam = WOCS_LANG !== 'ko' ? `?lang=${WOCS_LANG}` : '';
  var base = (function() {
    var scripts = document.querySelectorAll('script[src*="wocs-footer"]');
    if (scripts.length > 0) return scripts[0].getAttribute('src').replace('assets/js/wocs-footer.js', '');
    if (typeof WOCS_BASE !== 'undefined') return WOCS_BASE;
    return '';
  })();
  function href(p) {
    var clean = p.replace(/^\//, '');
    var b = base + clean;
    if (!langParam) return b;
    if (b.indexOf('#') >= 0) {
      var parts = b.split('#');
      return parts[0] + (parts[0].indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG + '#' + parts[1];
    }
    return b + (b.indexOf('?')>=0?'&':'?') + 'lang=' + WOCS_LANG;
  }
  el.className = 'cta-section';
  el.innerHTML = `
    <div style="max-width:700px;margin:0 auto" class="anim">
      <div class="slab">${tc('ctaReady')}</div>
      <h2 style="font-size:clamp(36px,5vw,64px);font-weight:300;margin-top:16px;line-height:1.15">
        <span class="shimmer-text">${tc('ctaTitle')}</span>
      </h2>
      <p class="font-body" style="font-size:15px;color:rgba(240,235,224,0.53);line-height:1.8;margin-top:24px">
        ${tc('ctaDesc')}
      </p>
      <div style="display:flex;gap:16px;justify-content:center;margin-top:40px">
        <a class="btn-gold-fill" href="${href('/contact/index.html')}">${tc('ctaBtn1')}</a>
        <a class="btn-gold" href="${href('/resources/downloads.html')}">${tc('ctaBtn2')}</a>
      </div>
    </div>`;
}

// ── Floating CTA buttons ──
function buildFloatingCTA() {
  const div = document.createElement('div');
  div.className = 'floating-cta';
  div.id = 'floating-cta';
  div.innerHTML = `
    <a href="tel:010-4337-0582" class="float-btn float-btn-gold" title="전화 문의" style="bottom:24px;right:24px;position:fixed;z-index:998">✆</a>
    <button class="float-btn float-btn-dark" onclick="window.scrollTo({top:0,behavior:'smooth'})" title="맨 위로" style="bottom:24px;right:84px;position:fixed;z-index:998">↑</button>
    <a href="https://wa.me/821043370582" class="chat-float" title="WhatsApp / 카카오톡" style="bottom:24px;right:144px;position:fixed;z-index:998" target="_blank">💬</a>`;
  document.body.appendChild(div);
  window.addEventListener('scroll', () => {
    const el = document.getElementById('floating-cta');
    if (el) el.classList.toggle('visible', window.scrollY > 600);
  }, { passive: true });
}

// ── Scroll Animation Observer ──
function initAnimations() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.anim').forEach(el => obs.observe(el));
}

// ── Noise Overlay ──
function addNoiseOverlay() {
  const div = document.createElement('div');
  div.className = 'noise-overlay';
  document.body.appendChild(div);
}

// ── Init All ──



document.addEventListener('DOMContentLoaded', () => {
  buildWocsFooter();
  buildFloatingCTA();
  addNoiseOverlay();
  translatePage();
  // Delay animation init to allow DOM to settle
  setTimeout(initAnimations, 100);
  // Build CTA if placeholder exists
  buildWocsCTA();
});

/* ═══ LIGHTBOX ═══ */
function initLightbox() {
  var imgs = document.querySelectorAll('[data-lightbox]');
  if (!imgs.length) return;
  
  var lb = document.createElement('div');
  lb.className = 'lightbox';
  lb.innerHTML = '<div class="lightbox-count"></div><div class="lightbox-close">✕</div><div class="lightbox-nav lightbox-prev">❮</div><div class="lightbox-nav lightbox-next">❯</div><img src="" alt="">';
  document.body.appendChild(lb);
  
  var lbImg = lb.querySelector('img');
  var lbCount = lb.querySelector('.lightbox-count');
  var currentIdx = 0;
  var gallery = [];
  
  imgs.forEach(function(img, i) {
    gallery.push(img.src);
    img.style.cursor = 'pointer';
    img.addEventListener('click', function() {
      currentIdx = i;
      showImage();
      lb.classList.add('active');
    });
  });
  
  function showImage() {
    lbImg.src = gallery[currentIdx];
    lbCount.textContent = (currentIdx + 1) + ' / ' + gallery.length;
  }
  
  lb.querySelector('.lightbox-close').addEventListener('click', function() { lb.classList.remove('active'); });
  lb.querySelector('.lightbox-prev').addEventListener('click', function() { currentIdx = (currentIdx - 1 + gallery.length) % gallery.length; showImage(); });
  lb.querySelector('.lightbox-next').addEventListener('click', function() { currentIdx = (currentIdx + 1) % gallery.length; showImage(); });
  lb.addEventListener('click', function(e) { if (e.target === lb) lb.classList.remove('active'); });
  document.addEventListener('keydown', function(e) {
    if (!lb.classList.contains('active')) return;
    if (e.key === 'Escape') lb.classList.remove('active');
    if (e.key === 'ArrowLeft') { currentIdx = (currentIdx - 1 + gallery.length) % gallery.length; showImage(); }
    if (e.key === 'ArrowRight') { currentIdx = (currentIdx + 1) % gallery.length; showImage(); }
  });
}

/* ═══ FAQ ACCORDION ═══ */
function initFAQ() {
  document.querySelectorAll('.faq-q').forEach(function(q) {
    q.addEventListener('click', function() {
      var a = this.nextElementSibling;
      var isOpen = this.classList.contains('open');
      // Close all
      document.querySelectorAll('.faq-q.open').forEach(function(oq) { oq.classList.remove('open'); oq.nextElementSibling.classList.remove('open'); });
      if (!isOpen) { this.classList.add('open'); a.classList.add('open'); }
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(initLightbox, 300);
  setTimeout(initFAQ, 300);
});

/* ═══ IMAGE CAROUSEL ═══ */
function initCarousels(){document.querySelectorAll('.carousel').forEach(function(c){var track=c.querySelector('.carousel-track');var slides=c.querySelectorAll('.carousel-slide');var dotsDiv=c.querySelector('.carousel-dots');if(!track||slides.length<2)return;var idx=0;function go(i){idx=(i+slides.length)%slides.length;track.style.transform='translateX(-'+(idx*100)+'%)';if(dotsDiv)dotsDiv.querySelectorAll('.carousel-dot').forEach(function(d,j){d.classList.toggle('active',j===idx)})}var prev=c.querySelector('.carousel-prev');var next=c.querySelector('.carousel-next');if(prev)prev.addEventListener('click',function(){go(idx-1)});if(next)next.addEventListener('click',function(){go(idx+1)});if(dotsDiv){slides.forEach(function(_,i){var dot=document.createElement('div');dot.className='carousel-dot'+(i===0?' active':'');dot.addEventListener('click',function(){go(i)});dotsDiv.appendChild(dot)})}setInterval(function(){go(idx+1)},5000)})}
document.addEventListener('DOMContentLoaded',function(){setTimeout(initCarousels,400)});

/* ═══ SHOWCASE SLIDER ═══ */
function initShowcase(){document.querySelectorAll('.showcase-slider').forEach(function(s){var slides=s.querySelectorAll('.showcase-slide');if(slides.length<2)return;var idx=0;function go(i){slides[idx].classList.remove('active');idx=(i+slides.length)%slides.length;slides[idx].classList.add('active')}var prev=s.querySelector('.sc-prev');var next=s.querySelector('.sc-next');if(prev)prev.addEventListener('click',function(){go(idx-1)});if(next)next.addEventListener('click',function(){go(idx+1)});setInterval(function(){go(idx+1)},6000)})}
document.addEventListener('DOMContentLoaded',function(){setTimeout(initShowcase,500)});

function initMatSliders(){document.querySelectorAll('.mat-slider').forEach(function(s){var track=s.querySelector('.mat-track');var cards=s.querySelectorAll('.mat-card');var dotsDiv=s.querySelector('.mat-dots');if(!track||cards.length<5)return;var perView=4;if(window.innerWidth<768)perView=2;var maxIdx=Math.ceil(cards.length/perView)-1;var idx=0;for(var i=0;i<=maxIdx;i++){var d=document.createElement('div');d.className='mat-dot'+(i===0?' active':'');d.dataset.i=i;d.addEventListener('click',function(){go(parseInt(this.dataset.i))});dotsDiv.appendChild(d)}function go(i){idx=Math.max(0,Math.min(i,maxIdx));track.style.transform='translateX(-'+(idx*100)+'%)';dotsDiv.querySelectorAll('.mat-dot').forEach(function(d,j){d.classList.toggle('active',j===idx)})}setInterval(function(){go((idx+1)%(maxIdx+1))},5000)})}
document.addEventListener('DOMContentLoaded',function(){setTimeout(initMatSliders,500)});
