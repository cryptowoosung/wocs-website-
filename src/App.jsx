import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import ReactDOM from 'react-dom/client'

import TR_KO from './locales/ko.js';

// Lazy loaders for non-Korean locales. Each returns the plain JS object
// stored in src/locales/<lang>.js. Keeps initial bundle small.
const TR_LOADERS = {
  en: () => import('./locales/en.js').then((m) => m.default),
  ja: () => import('./locales/ja.js').then((m) => m.default),
  zh: () => import('./locales/zh.js').then((m) => m.default),
  es: () => import('./locales/es.js').then((m) => m.default),
  fr: () => import('./locales/fr.js').then((m) => m.default),
  de: () => import('./locales/de.js').then((m) => m.default),
  pt: () => import('./locales/pt.js').then((m) => m.default),
  it: () => import('./locales/it.js').then((m) => m.default),
  ar: () => import('./locales/ar.js').then((m) => m.default),
  ru: () => import('./locales/ru.js').then((m) => m.default),
  tr: () => import('./locales/tr.js').then((m) => m.default),
  tw: () => import('./locales/tw.js').then((m) => m.default),
  id: () => import('./locales/id.js').then((m) => m.default),
  th: () => import('./locales/th.js').then((m) => m.default),
};

// ============================================
// 기존 index.html의 <script type="text/babel">
// 블록에서 추출한 JSX 코드
// Phase 2A: 최소 수정 이식
// Phase 2C: inline style → CSS 클래스 리팩터 예정
// ============================================

// [Phase 2B] Removed UMD destructuring: const { useState, useEffect, useRef, useCallback } = React;

/* ═══════════════════════════════════════════════════════════════
   WOCS MODULAR STRUCTURES — Complete Premium Homepage
   Benchmarked: Luna Glamping (tech-forward hero + dome selector + B2B)
              + Glitzcamp (product grid + cases + 6-step + mega footer)
   Aesthetic: Dark Luxury — Obsidian + Antique Gold + Warm Ivory
   Fonts: Cormorant Garamond (display) + Lexend (body)
   ═══════════════════════════════════════════════════════════════ */

const GOLD = "#c9a96e";
const GOLD_L = "#e4d5a8";
const IVORY = "#f0ebe0";
const BG = "#09090b";
const BG2 = "#111113";
const BG3 = "#18181b";

function WOCSHomepage() {
  const [scrollY, setScrollY] = useState(0);
  const [heroIdx, setHeroIdx] = useState(0);
  const [megaNav, setMegaNav] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeDome, setActiveDome] = useState(2);
  const [activeProduct, setActiveProduct] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [activeCase, setActiveCase] = useState(0);
  const [hovOccasion, setHovOccasion] = useState(null);
  const [activeReview, setActiveReview] = useState(0);
  const [vis, setVis] = useState(new Set());
  const [counting, setCounting] = useState(false);
  const [counts, setCounts] = useState([0,0,0,0]);
  const [emailVal, setEmailVal] = useState("");
  const [langOpen, setLangOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get("lang");
    if (urlLang) { try { localStorage.setItem("wocs-lang", urlLang); } catch(e){} return urlLang; }
    try { const stored = localStorage.getItem("wocs-lang"); if (stored) return stored; } catch(e){}
    return "ko";
  });
  const langRef = useRef(null);

  // Scroll listener
  useEffect(() => {
    const h = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", h, { passive: true });
    return () => window.removeEventListener("scroll", h);
  }, []);

  // Intersection Observer for animations
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => entries.forEach(e => {
        if (e.isIntersecting) setVis(p => new Set([...p, e.target.dataset.s]));
      }),
      { threshold: 0.1 }
    );
    setTimeout(() => {
      document.querySelectorAll("[data-s]").forEach(el => obs.observe(el));
    }, 100);
    return () => obs.disconnect();
  }, []);

  // Hero auto-slide
  useEffect(() => {
    const t = setInterval(() => setHeroIdx(p => (p + 1) % heroSlides.length), 6000);
    return () => clearInterval(t);
  }, []);

  // Review auto-slide
  useEffect(() => {
    const t = setInterval(() => setActiveReview(p => (p + 1) % reviews.length), 5000);
    return () => clearInterval(t);
  }, []);

  // Mobile menu: body scroll lock
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  // Mobile menu: close on outside click
  useEffect(() => {
    if (!mobileOpen) return;
    const handleClick = (e) => {
      if (!e.target.closest("header")) setMobileOpen(false);
    };
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, [mobileOpen]);

  // Counter animation
  useEffect(() => {
    if (!vis.has("stats") || counting) return;
    setCounting(true);
    const tgts = [16, 120, 500, 98];
    let f = 0;
    const iv = setInterval(() => {
      f++;
      const p = Math.min(f / 50, 1);
      const e = 1 - Math.pow(1 - p, 3);
      setCounts(tgts.map(t => Math.round(t * e)));
      if (f >= 50) clearInterval(iv);
    }, 35);
  }, [vis, counting]);

  // Close language popup on outside click
  useEffect(() => {
    const handler = (e) => {
      if (langRef.current && !langRef.current.contains(e.target)) {
        setLangOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleLangSelect = (code) => {
    setCurrentLang(code);
    setLangOpen(false);
    try { localStorage.setItem("wocs-lang", code); } catch(e){}
    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set("lang", code);
    window.history.replaceState({}, "", url);
  };

  const sv = (id) => vis.has(id);

  // ─── DATA ───────────────────────────────────────────
  // ═══════════════════════════════════════════════════════
  // COMPREHENSIVE i18n TRANSLATION SYSTEM
  // ═══════════════════════════════════════════════════════
  // i18n lazy loader — only 'ko' is shipped in the initial bundle.
  // Other languages are fetched on demand when currentLang changes.
  const [trCache, setTrCache] = useState({ ko: TR_KO });

  useEffect(() => {
    if (trCache[currentLang]) return;
    const loader = TR_LOADERS[currentLang];
    if (!loader) return;
    let cancelled = false;
    loader()
      .then((data) => {
        if (!cancelled) setTrCache((prev) => ({ ...prev, [currentLang]: data }));
      })
      .catch((err) => {
        console.warn('[i18n] failed to load locale', currentLang, err);
      });
    return () => {
      cancelled = true;
    };
  }, [currentLang, trCache]);

  const TR = trCache;

  // Translation helper — fallback to Korean

  // Translation helper — fallback to Korean
  const t = (key) => {
    const lang = TR[currentLang] || TR["ko"];
    return lang[key] || TR["ko"][key] || key;
  };

  // ═══════════════════════════════════════════════════════
  // DATA ARRAYS — All using t() for full i18n
  // ═══════════════════════════════════════════════════════
  const heroSlides = [
    { tag: t("heroTag1"), title: t("heroTitle1"), sub: t("heroSub1"), cta: t("heroCta1"), img: "assets/images/17-d600-ext.webp", w: 1536, h: 1024, href: "products/geodesic-domes.html" },
    { tag: t("heroTag2"), title: t("heroTitle2"), sub: t("heroSub2"), cta: t("heroCta2"), img: "assets/images/01-ex15-ext.webp", w: 1456, h: 816, href: "products/safari-tents.html" },
    { tag: t("heroTag3"), title: t("heroTitle3"), sub: t("heroSub3"), cta: t("heroCta3"), img: "assets/images/22-sig-o-ext.webp", w: 1456, h: 816, href: "products/luxury-tents.html" },
    { tag: t("heroTag4"), title: t("heroTitle4"), sub: t("heroSub4"), cta: t("heroCta4"), img: "assets/images/50-resort-mountain.webp", w: 1456, h: 816, href: "products/modular-systems.html" },
  ];

  const navItems = [
    { label: t("navProducts"), scrollTo: "products", href: "products/index.html", mega: [
      { title: t("megaGeoDomes"), titleHref: "products/geodesic-domes.html", links: [
        {text: t("megaCustomDomes"), href: "products/geodesic-domes-custom.html"},
        {text: t("megaPreconfigured"), href: "products/geodesic-domes-preconfigured.html"},
        {text: t("megaReadyShip"), href: "products/geodesic-domes-ready.html"},
      ]},
      { title: t("megaSafariTents"), titleHref: "products/safari-tents.html", links: [
        {text: t("megaBasic"), href: "products/safari-basic.html"},
        {text: t("megaExtreme"), href: "products/safari-extreme.html"},
        {text: t("megaCabin"), href: "products/safari-cabin.html"},
        {text: t("megaElite"), href: "products/safari-elite.html"},
        {text: t("megaLuxury"), href: "products/safari-luxury.html"},
      ]},
      { title: t("megaLuxuryTents"), titleHref: "products/luxury-tents.html", links: [
        {text: t("megaSignature_O"), href: "products/cocoon-house.html"},
        {text: t("megaSignature_A"), href: "products/sailing-tent.html"},
        {text: t("megaSignature_P"), href: "products/birdcage.html"},
        {text: t("megaPeakLodge"), href: "products/peak-lodge.html"},
        {text: t("megaNordicTipi"), href: "products/nordic-tipi.html"},
        {text: t("megaCubeCabin"), href: "products/cube-cabin.html"},
        {text: t("megaBellTents"), href: "products/bell-tent.html"},
        {text: t("megaDomeTents"), href: "products/dome-tent.html"},
      ]},
      { title: t("megaAccessories"), titleHref: "products/modular-systems.html", links: [
        {text: t("megaModUnits"), href: "products/modular-units.html"},
        {text: t("megaModBath"), href: "products/modular-bath.html"},
        {text: t("megaModDeck"), href: "products/modular-deck.html"},
        {text: t("megaSolar"), href: "products/solar-system.html"},
        {text: t("megaAddons"), href: "products/addons.html"},
      ]},
    ]},
    { label: t("navOccasions"), scrollTo: "occasions", href: "occasions/index.html", mega: [
      { title: "", links: [
        {text: t("megaAirbnb"), href: "occasions/airbnb.html"},
        {text: t("megaResort"), href: "occasions/resort.html"},
        {text: t("megaWedding"), href: "occasions/wedding.html"},
        {text: t("megaHotel"), href: "occasions/hotel.html"},
        {text: t("megaHunting"), href: "occasions/glamping.html"},
        {text: t("megaGlampPod"), href: "occasions/glamping-pod.html"},
        {text: t("megaLuxCamp"), href: "occasions/glamping.html#luxury"},
        {text: t("megaPermanent"), href: "occasions/permanent.html"},
        {text: t("megaSports"), href: "occasions/sports.html"},
        {text: t("megaWinterCamp"), href: "occasions/winter.html"},
      ]},
    ]},
    { label: t("navProject"), scrollTo: "project", href: "project/index.html", mega: [
      { title: t("megaPlanning"), links: [
        {text: t("megaPlanCases"), href: "project/planning-cases.html"},
        {text: t("megaStartBiz"), href: "project/start-business.html"},
        {text: t("megaBuyLand"), href: "project/buying-land.html"},
      ]},
      { title: t("megaPartnership"), links: [
        {text: t("megaFinancing"), href: "project/financing.html"},
        {text: t("megaRevShare"), href: "project/revenue-sharing.html"},
        {text: t("megaMultiOrder"), href: "contact/index.html"},
        {text: t("megaROI"), href: "contact/roi-calculator.html"},
      ]},
    ]},
    { label: t("navResources"), scrollTo: "resources", href: "resources/index.html", mega: [
      { title: "", links: [
        {text: t("megaFAQs"), href: "resources/faq.html"},
        {text: t("megaBlog"), href: "resources/blog.html"},
        {text: t("megaDownloads"), href: "resources/downloads.html"},
        {text: t("megaReviewsLink"), href: "resources/reviews.html"},
        {text: t("megaDealer"), href: "resources/dealer.html"},
        {text: t("megaTeam"), href: "about/team.html"},
      ]},
    ]},
    { label: t("navGallery"), scrollTo: "gallery", href: "gallery/index.html" },
    { label: t("navPortfolio"), scrollTo: "cases", href: "portfolio/index.html" },
    { label: "WOCS" + (currentLang === "ko" ? "소개" : currentLang === "ja" ? "紹介" : currentLang === "zh" || currentLang === "tw" ? "簡介" : " About"), scrollTo: "about", href: "about/index.html" },
    { label: t("navContact"), scrollTo: "contact", href: "contact/index.html" },
  ];

  const scrollToSection = (id) => {
    setMegaNav(null);
    const el = document.getElementById(id);
    if (el) {
      const y = el.getBoundingClientRect().top + window.pageYOffset - 110;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  const productCards = [
    { name: t("pcName1"), sub: t("pcSub1"), img: "assets/images/s-classic.webp", w: 1456, h: 816, href: "products/safari-tents.html" },
    { name: t("pcName2"), sub: t("pcSub2"), img: "assets/images/19-d800-ext.webp", w: 1456, h: 816, href: "products/geodesic-domes.html" },
    { name: t("pcName3"), sub: t("pcSub3"), img: "assets/images/22-sig-o-ext.webp", w: 1456, h: 816, href: "products/luxury-tents.html" },
    { name: t("pcName4"), sub: t("pcSub4"), img: "assets/images/42-modular-unit.webp", w: 1456, h: 816, href: "products/modular-systems.html" },
  ];

  const domeSizes = [
    { s: "5m", area: "19.6㎡", people: "2", desc: t("domeDesc1"), price: "₩" },
    { s: "6m", area: "28.3㎡", people: "2~3", desc: t("domeDesc2"), price: "₩₩" },
    { s: "7m", area: "38.5㎡", people: "3~4", desc: t("domeDesc3"), price: "₩₩" },
    { s: "8m", area: "50.3㎡", people: "4~5", desc: t("domeDesc4"), price: "₩₩₩" },
    { s: "9m", area: "63.6㎡", people: "5~6", desc: t("domeDesc5"), price: "₩₩₩" },
    { s: "10m", area: "78.5㎡", people: "6~8", desc: t("domeDesc6"), price: "₩₩₩₩" },
    { s: "12m", area: "113㎡", people: "10+", desc: t("domeDesc7"), price: "₩₩₩₩" },
    { s: "15m", area: "177㎡", people: "20+", desc: t("domeDesc8"), price: "₩₩₩₩₩" },
  ];

  const productSections = [
    { tag: t("prodTag1"), label: t("prodLabel1"), desc: t("prodDesc1"), features: [t("prodFeat1a"), t("prodFeat1b"), t("prodFeat1c"), t("prodFeat1d")], cta: t("prodCta1") },
    { tag: t("prodTag2"), label: t("prodLabel2"), desc: t("prodDesc2"), features: [t("prodFeat2a"), t("prodFeat2b"), t("prodFeat2c"), t("prodFeat2d")], cta: t("prodCta2") },
    { tag: t("prodTag3"), label: t("prodLabel3"), desc: t("prodDesc3"), features: [t("prodFeat3a"), t("prodFeat3b"), t("prodFeat3c"), t("prodFeat3d")], cta: t("prodCta3") },
    { tag: t("prodTag4"), label: t("prodLabel4"), desc: t("prodDesc4"), features: [t("prodFeat4a"), t("prodFeat4b"), t("prodFeat4c"), t("prodFeat4d")], cta: t("prodCta4") },
  ];

  const cases = [
    { country: t("caseCountry1"), name: t("caseName1"), desc: t("caseDesc1"), href: "portfolio/index.html" },
    { country: t("caseCountry2"), name: t("caseName2"), desc: t("caseDesc2"), href: "portfolio/index.html" },
    { country: t("caseCountry3"), name: t("caseName3"), desc: t("caseDesc3"), href: "portfolio/index.html" },
    { country: t("caseCountry4"), name: t("caseName4"), desc: t("caseDesc4"), href: "portfolio/index.html" },
    { country: t("caseCountry5"), name: t("caseName5"), desc: t("caseDesc5"), href: "portfolio/index.html" },
  ];

  const steps = [
    { n: "01", title: t("step1"), desc: t("step1d"), svg: '<path d="M8 38V22a2 2 0 012-2h10a2 2 0 012 2v16"/><path d="M26 38V14a2 2 0 012-2h10a2 2 0 012 2v24"/><path d="M18 28h8"/><circle cx="14" cy="14" r="4"/><path d="M14 18v-0"/>' },
    { n: "02", title: t("step2"), desc: t("step2d"), svg: '<path d="M24 4C17.4 4 12 9.4 12 16c0 9 12 24 12 24s12-15 12-24c0-6.6-5.4-12-12-12z"/><circle cx="24" cy="16" r="5"/>' },
    { n: "03", title: t("step3"), desc: t("step3d"), svg: '<rect x="8" y="6" width="32" height="36" rx="2"/><path d="M16 14h16M16 22h16M16 30h10"/><path d="M30 28l4 4 6-8"/>' },
    { n: "04", title: t("step4"), desc: t("step4d"), svg: '<path d="M6 42L24 6l18 36H6z"/><path d="M15 42V24l9-6 9 6v18"/><path d="M24 30v12"/><path d="M20 34h8"/>' },
    { n: "05", title: t("step5"), desc: t("step5d"), svg: '<path d="M30 18c0-3.3-2.7-6-6-6s-6 2.7-6 6"/><path d="M16 28h16"/><rect x="10" y="8" width="28" height="32" rx="2"/><path d="M18 20h12M18 24h8M18 32h12M18 36h6"/>' },
    { n: "06", title: t("step6"), desc: t("step6d"), svg: '<path d="M24 4v8M4 24h8M36 24h8M10 10l6 6M32 10l-6 6"/><circle cx="24" cy="24" r="8"/><path d="M20 44h8"/><path d="M24 32v12"/>' },
    { n: "07", title: t("step7"), desc: t("step7d"), svg: '<path d="M8 24l8-12h16l8 12-8 12H16L8 24z"/><circle cx="24" cy="24" r="6"/><path d="M34 12l6-6M34 36l6 6M14 12l-6-6M14 36l-6 6"/>' },
    { n: "08", title: t("step8"), desc: t("step8d"), svg: '<path d="M20 8l-2-4h-4l-2 4-4 2v4l-4 2 2 4-2 4 4 2v4l4 2 2 4h4l2-4 4-2v-4l4-2-2-4 2-4-4-2v-4l-4-2z"/><circle cx="20" cy="24" r="6"/><path d="M32 16l8-8M36 8h4v4"/>' },
  ];

  const occasions = [
    { img: "assets/images/15-lodge-lx-ext.webp", w: 1024, h: 1024, name: t("occ1"), href: "occasions/glamping.html" },
    { img: "assets/images/50-resort-mountain.webp", w: 1456, h: 816, name: t("occ2"), href: "occasions/resort.html" },
    { img: "assets/images/s-classic.webp", w: 1456, h: 816, name: t("occ3"), href: "occasions/airbnb.html" },
    { img: "assets/images/26-sig-p-ext.webp", w: 1456, h: 816, name: t("occ4"), href: "occasions/wedding.html" },
    { img: "assets/images/19-d800-ext.webp", w: 1456, h: 816, name: t("occ5"), href: "occasions/sports.html" },
    { img: "assets/images/17-d600-ext.webp", w: 1536, h: 1024, name: t("occ6"), href: "occasions/glamping-pod.html" },
    { img: "assets/images/35-sig-q-ext.webp", w: 1456, h: 816, name: t("occ7"), href: "occasions/permanent.html" },
    { img: "assets/images/02-ex25-ext.webp", w: 1456, h: 816, name: t("occ8"), href: "occasions/winter.html" },
    { img: "assets/images/50-resort-mountain3.webp", w: 1456, h: 816, name: t("occ9"), href: "occasions/index.html" },
    { img: "assets/images/28-sig-h-ext.webp", w: 1456, h: 816, name: t("occ10"), href: "occasions/index.html" },
  ];

  const features = [
    { svg: '<circle cx="24" cy="24" r="16"/><path d="M24 12v24M12 24h24"/><path d="M16 16l16 16M32 16L16 32"/>', title: t("feat1"), desc: t("feat1d") },
    { svg: '<rect x="8" y="20" width="32" height="16" rx="2"/><path d="M16 20V12a8 8 0 0116 0v8"/><circle cx="24" cy="28" r="3"/>', title: t("feat2"), desc: t("feat2d") },
    { svg: '<path d="M24 4l6 12h14l-11 8 4 14-13-9-13 9 4-14L4 16h14z"/>', title: t("feat3"), desc: t("feat3d") },
    { svg: '<path d="M12 8h24l-4 32H16L12 8z"/><path d="M10 8h28"/><path d="M20 16v16M28 16v16M16 24h16"/>', title: t("feat4"), desc: t("feat4d") },
  ];

  const reviews = [
    { name: "Lee W.", loc: "California, USA", stars: 5, text: t("review1") },
    { name: "Amy R.", loc: "Ontario, Canada", stars: 5, text: t("review2") },
    { name: "Ella K.", loc: "Sydney, Australia", stars: 5, text: t("review3") },
    { name: "Peter M.", loc: "London, UK", stars: 5, text: t("review4") },
  ];

  const badges = [
    { icon: "🏔", label: t("badge1") }, { icon: "🛋", label: t("badge2") },
    { icon: "🛡", label: t("badge3") }, { icon: "🔒", label: t("badge4") },
    { icon: "⚙", label: t("badge5") },
  ];

  const blogs = [
    { tag: t("blogTag1"), title: t("blogTitle1"), ko: t("blogKo1"), img: "assets/images/01-ex15-ext.webp", w: 1456, h: 816, href: "resources/blog.html" },
    { tag: t("blogTag2"), title: t("blogTitle2"), ko: t("blogKo2"), img: "assets/images/22-sig-o-ext.webp", w: 1456, h: 816, href: "resources/blog.html" },
    { tag: t("blogTag3"), title: t("blogTitle3"), ko: t("blogKo3"), img: "assets/images/50-resort-mountain.webp", w: 1456, h: 816, href: "resources/blog.html" },
  ];

  // Language / Flag data
  const languages = [
    { code: "ko", cc: "KR", label: "한국어", color: "#003478", accent: "#CD2E3A", x: 72, y: -10 },
    { code: "en", cc: "US", label: "English", color: "#3C3B6E", accent: "#B22234", x: 10, y: 65 },
    { code: "ja", cc: "JP", label: "日本語", color: "#fff", accent: "#BC002D", x: -55, y: -20 },
    { code: "zh", cc: "CN", label: "中文", color: "#DE2910", accent: "#FFDE00", x: -40, y: 55 },
    { code: "es", cc: "ES", label: "Español", color: "#C60B1E", accent: "#FFC400", x: 55, y: 80 },
    { code: "fr", cc: "FR", label: "Français", color: "#002395", accent: "#ED2939", x: -15, y: -65 },
    { code: "de", cc: "DE", label: "Deutsch", color: "#000", accent: "#DD0000", x: -70, y: 25 },
    { code: "pt", cc: "PT", label: "Português", color: "#006600", accent: "#FF0000", x: 75, y: 40 },
    { code: "it", cc: "IT", label: "Italiano", color: "#008C45", accent: "#CD212A", x: -60, y: -50 },
    { code: "ar", cc: "SA", label: "العربية", color: "#006C35", accent: "#fff", x: -30, y: 85 },
    { code: "ru", cc: "RU", label: "Русский", color: "#0039A6", accent: "#D52B1E", x: 60, y: -50 },
    { code: "tr", cc: "TR", label: "Türkçe", color: "#E30A17", accent: "#fff", x: 30, y: 95 },
    { code: "tw", cc: "TW", label: "繁體中文", color: "#FE0000", accent: "#000095", x: 80, y: -40 },
    { code: "id", cc: "ID", label: "Bahasa", color: "#CE1126", accent: "#fff", x: -75, y: 65 },
    { code: "th", cc: "TH", label: "ไทย", color: "#A51931", accent: "#2D2A4A", x: -85, y: -5 },
  ];

  const flagCircle = (lang, size = 28) => (
    <div style={{
      width: size, height: size, borderRadius: "50%",
      overflow: "hidden", flexShrink: 0,
      background: `linear-gradient(135deg, ${lang.color}, ${lang.accent})`,
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <img
        src={`https://flagcdn.com/w80/${lang.cc.toLowerCase()}.png`}
        alt={lang.label}
        style={{
          width: size * 1.4, height: size * 1.4,
          objectFit: "cover", objectPosition: "center",
          display: "block",
        }}
        onError={(e) => {
          e.target.style.display = "none";
          e.target.parentElement.innerHTML = `<span style="font-size:${Math.max(size * 0.32, 8)}px;font-weight:700;color:#fff;font-family:'Lexend',sans-serif;letter-spacing:0.5px;text-shadow:0 1px 2px rgba(0,0,0,.5)">${lang.cc}</span>`;
        }}
      />
    </div>
  );

  const statsData = [
    { val: counts[0], suffix: "+", label: "Years Experience", ko: t("statsYears") },
    { val: counts[1], suffix: "+", label: "Countries Shipped", ko: t("statsCountries") },
    { val: counts[2], suffix: "+", label: "Projects Completed", ko: t("statsProjects") },
    { val: counts[3], suffix: "%", label: "Client Satisfaction", ko: t("statsSat") },
  ];

  // ─── STYLES ────────────────────────────────────────
  const S = {
    root: { fontFamily: "'Cormorant Garamond', 'Noto Serif KR', serif", background: BG, color: IVORY, minHeight: "100vh", overflowX: "hidden" },
    sf: { fontFamily: "'Lexend', 'Noto Sans KR', sans-serif" },
    slab: { fontFamily: "'Lexend', sans-serif", fontSize: 10, fontWeight: 500, letterSpacing: 5, textTransform: "uppercase", color: GOLD },
  };

  // Animation helper
  const anim = (id, type = "fu", delay = 0) => ({
    "data-s": id,
    style: {
      opacity: sv(id) ? 1 : 0,
      transform: sv(id)
        ? "none"
        : type === "fu" ? "translateY(50px)"
        : type === "fr" ? "translateX(-50px)"
        : type === "fl" ? "translateX(50px)"
        : "scale(0.93)",
      transition: `all 0.85s cubic-bezier(0.16,1,0.3,1) ${delay}s`,
    },
  });

  return (
    <div style={S.root}>
      {/* Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500&family=Lexend:wght@200;300;400;500;600&family=Noto+Sans+KR:wght@300;400;500;600&family=Noto+Serif+KR:wght@300;400;500;600&display=swap');
        * { margin:0; padding:0; box-sizing:border-box; }
        html { scroll-behavior: smooth; scroll-padding-top: 120px; }
        ::selection { background: ${GOLD}44; color: ${IVORY}; }

        @keyframes heroFade { from{opacity:0;transform:scale(1.05)} to{opacity:1;transform:scale(1)} }
        @keyframes shimmer { 0%{background-position:-200% center} 100%{background-position:200% center} }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes rotate { from{transform:rotate(0)} to{transform:rotate(360deg)} }
        @keyframes marquee { from{transform:translateX(0)} to{transform:translateX(-50%)} }
        @keyframes pulse { 0%,100%{opacity:.6} 50%{opacity:1} }
        @keyframes slideUp { from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:none} }
        @keyframes flagPop { from{opacity:0;transform:scale(0) translate(0,0)} to{opacity:1;transform:scale(1)} }
        @keyframes globeSpin { 0%{transform:rotateY(0)} 100%{transform:rotateY(360deg)} }
        @keyframes flagFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        @keyframes ringPulse { 0%{transform:scale(1);opacity:.3} 100%{transform:scale(2.2);opacity:0} }

        .gold-text { background:linear-gradient(135deg,${GOLD},${GOLD_L},${GOLD}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
        .shimmer-text { background:linear-gradient(90deg,${GOLD} 0%,#f5e6c8 25%,${GOLD} 50%,#f5e6c8 75%,${GOLD} 100%); background-size:200% auto; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation:shimmer 4s linear infinite; }
        .btn-gold { font-family:'Lexend',sans-serif; font-size:11px; font-weight:500; letter-spacing:3px; text-transform:uppercase; padding:16px 40px; border:1px solid ${GOLD}; color:${GOLD}; background:transparent; cursor:pointer; transition:all .4s; position:relative; overflow:hidden; }
        .btn-gold:hover { background:${GOLD}; color:${BG}; }
        .btn-gold-fill { font-family:'Lexend',sans-serif; font-size:11px; font-weight:500; letter-spacing:3px; text-transform:uppercase; padding:16px 40px; border:1px solid ${GOLD}; color:${BG}; background:${GOLD}; cursor:pointer; transition:all .4s; }
        .btn-gold-fill:hover { background:transparent; color:${GOLD}; }
        .section-pad { padding:120px 5%; max-width:1400px; margin:0 auto; }
        .noise-overlay { display:none; }
        @media(max-width:768px){
          .section-pad{padding:60px 4% !important}
          #root{overflow-x:hidden}
        }
      `}</style>

      {/* Noise overlay */}
      <div className="noise-overlay" />

      {/* ═══════════ 1. HEADER / GNB ═══════════ */}
      <header style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000,
        background: scrollY > 80 ? `${BG}ee` : "transparent",
        backdropFilter: scrollY > 80 ? "blur(20px)" : "none",
        borderBottom: scrollY > 80 ? `1px solid ${GOLD}15` : "none",
        transition: "all .5s",
      }}>
        {/* Top bar */}
        <div style={{ borderBottom: `1px solid ${GOLD}10`, padding: "8px 5%", display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 24, ...S.sf, fontSize: 11, color: `${IVORY}88`, letterSpacing: 1 }}>
          <span><a href="tel:01043370582" style={{color:'inherit',textDecoration:'none'}}>✆ 010-4337-0582</a></span>
          <span><a href="mailto:info@wocs.kr" style={{color:'inherit',textDecoration:'none'}}>info@wocs.kr</a></span>
        </div>
        {/* Main nav */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 5%", height: 70 }}>
          {/* Logo */}
          <div
            role="link"
            tabIndex={0}
            onClick={() => {
              const p = window.location.pathname;
              const atHome = p === "/" || p.endsWith("/index.html") || p.endsWith("/vite-index.html");
              if (atHome) {
                window.scrollTo({ top: 0, behavior: "smooth" });
                setMobileOpen(false);
                setMegaNav(null);
              } else {
                window.location.href = "/?lang=" + currentLang;
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                e.currentTarget.click();
              }
            }}
            style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}
          >
            <div style={{
              width: 40, height: 40, border: `2px solid ${GOLD}`,
              transform: "rotate(45deg)", display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <span style={{ transform: "rotate(-45deg)", fontWeight: 700, fontSize: 18, color: GOLD }}>W</span>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 20, letterSpacing: 4, color: IVORY }}>WOCS</div>
              <div style={{ ...S.sf, fontSize: 8, letterSpacing: 4, color: GOLD, marginTop: -2 }}>MODULAR STRUCTURES</div>
            </div>
          </div>

          {/* Desktop Nav */}
          <nav className={`nav-list ${mobileOpen ? "mobile-open" : ""}`}>
            {navItems.map((item, i) => (
              <div key={i}
                className="nav-item"
                onMouseEnter={() => !mobileOpen && item.mega && setMegaNav(i)}
                onMouseLeave={() => !mobileOpen && setMegaNav(null)}
                style={{ position: "relative" }}
              >
                <button className="nav-link" onClick={() => {
                  if (mobileOpen && item.mega) { setMegaNav(megaNav === i ? null : i); return; }
                  setMegaNav(null); setMobileOpen(false);
                  if (item.href && !item.mega) {
                    window.location.href = item.href + (item.href.indexOf("?")>=0?"&":"?") + "lang=" + currentLang;
                  } else if (item.scrollTo) {
                    scrollToSection(item.scrollTo);
                  }
                }} style={{
                  ...S.sf, fontSize: 12, fontWeight: 400, letterSpacing: 2, textTransform: "uppercase",
                  color: megaNav === i ? GOLD : `${IVORY}cc`, background: "none", border: "none",
                  cursor: "pointer", padding: "24px 16px", transition: "color .3s",
                }}>
                  {item.label}
                  {item.mega && <span style={{ fontSize: 8, marginLeft: 4 }}>▾</span>}
                </button>

                {/* Mega dropdown */}
                {item.mega && megaNav === i && (
                  <div
                    onMouseEnter={() => setMegaNav(i)}
                    onMouseLeave={() => setMegaNav(null)}
                    className="mega-menu"
                    style={{
                      position: mobileOpen ? "static" : "absolute",
                      top: mobileOpen ? "auto" : "100%",
                      left: mobileOpen ? "auto" : "50%",
                      transform: mobileOpen ? "none" : "translateX(-50%)",
                      background: mobileOpen ? "rgba(201,169,110,0.04)" : `${BG}f5`,
                      backdropFilter: mobileOpen ? "none" : "blur(30px)",
                      border: mobileOpen ? "none" : `1px solid ${GOLD}20`,
                      borderLeft: mobileOpen ? `2px solid ${GOLD}33` : "none",
                      padding: mobileOpen ? "8px 0 8px 16px" : 32,
                      minWidth: mobileOpen ? 0 : (item.mega.length > 1 ? 600 : 280),
                      width: mobileOpen ? "100%" : "auto",
                      display: "flex",
                      flexDirection: mobileOpen ? "column" : "row",
                      gap: mobileOpen ? 4 : 40,
                      animation: mobileOpen ? "none" : "slideUp .3s ease forwards",
                    }}
                  >
                    {item.mega.map((col, ci) => (
                      <div key={ci}>
                        {col.title && (col.titleHref ? <a href={col.titleHref} style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 16, textTransform: "uppercase", display: "block", textDecoration: "none", cursor: "pointer" }}>{col.title}</a> : <div style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 16, textTransform: "uppercase" }}>{col.title}</div>)}
                        {col.links.map((link, li) => {
                          const linkText = typeof link === "object" ? link.text : link;
                          const linkHref = typeof link === "object" ? link.href : null;
                          const pm = linkText.match(/^(S-[A-Za-z ]+(?:EX|LX)?|Signature-[A-Z])\s*\((.+)\)$/);
                          const mainLabel = pm ? pm[1] : linkText;
                          const subLabel = pm ? pm[2] : null;
                          const inner = <>{mainLabel}{subLabel && <span style={{display:"block",fontSize:"0.7em",color:`${IVORY}55`,marginTop:2,fontWeight:300,letterSpacing:"0.3px"}}>{subLabel}</span>}</>;
                          return linkHref ? (
                            <a key={li} href={linkHref} style={{
                              ...S.sf, fontSize: 13, color: `${IVORY}bb`, padding: "7px 0",
                              cursor: "pointer", transition: "all .2s", borderBottom: `1px solid ${GOLD}08`,
                              display: "block", textDecoration: "none",
                            }}
                            onMouseEnter={e => { e.currentTarget.style.color = GOLD; e.currentTarget.style.paddingLeft = "8px"; }}
                            onMouseLeave={e => { e.currentTarget.style.color = `${IVORY}bb`; e.currentTarget.style.paddingLeft = "0"; }}
                            onClick={() => { setMobileOpen(false); setMegaNav(null); }}
                            >{inner}</a>
                          ) : (
                            <div key={li} style={{
                              ...S.sf, fontSize: 13, color: `${IVORY}bb`, padding: "7px 0",
                              cursor: "pointer", transition: "all .2s", borderBottom: `1px solid ${GOLD}08`,
                            }}
                            onMouseEnter={e => { e.currentTarget.style.color = GOLD; e.currentTarget.style.paddingLeft = "8px"; }}
                            onMouseLeave={e => { e.currentTarget.style.color = `${IVORY}bb`; e.currentTarget.style.paddingLeft = "0"; }}
                            >{inner}</div>
                          );
                        })}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            <button className="btn-gold" style={{ marginLeft: 20, padding: "10px 24px", fontSize: 10 }} onClick={() => window.location.href="contact/index.html?lang="+currentLang}>
              {t("getQuote")}
            </button>

            {/* ── Globe Language Selector (Glitzcamp Style) ── */}
            <div ref={langRef} style={{ position: "relative", marginLeft: 16 }}>
              {/* Globe button */}
              <button
                onClick={() => setLangOpen(!langOpen)}
                style={{
                  width: 42, height: 42, borderRadius: "50%",
                  border: `1.5px solid ${langOpen ? GOLD : `${IVORY}44`}`,
                  background: langOpen ? `${GOLD}18` : "transparent",
                  cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
                  transition: "all .4s", position: "relative", overflow: "visible",
                }}
                onMouseEnter={e => { if (!langOpen) e.currentTarget.style.borderColor = GOLD; }}
                onMouseLeave={e => { if (!langOpen) e.currentTarget.style.borderColor = `${IVORY}44`; }}
              >
                {/* Globe SVG icon */}
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={langOpen ? GOLD : `${IVORY}bb`} strokeWidth="1.5" style={{ transition: "stroke .3s" }}>
                  <circle cx="12" cy="12" r="10" />
                  <ellipse cx="12" cy="12" rx="4.5" ry="10" />
                  <path d="M2 12h20" />
                  <path d="M12 2c3 3.5 3 14.5 0 20" opacity=".4" />
                  <path d="M12 2c-3 3.5-3 14.5 0 20" opacity=".4" />
                  <path d="M4 7h16" opacity=".3" />
                  <path d="M4 17h16" opacity=".3" />
                </svg>

                {/* Current language badge */}
                <span style={{
                  position: "absolute", bottom: -4, right: -4,
                  filter: "drop-shadow(0 1px 3px rgba(0,0,0,.7))",
                }}>
                  {flagCircle(languages.find(l => l.code === currentLang), 16)}
                </span>
              </button>

              {/* ── Expanded Flag Cloud ── */}
              {langOpen && (
                <div style={{
                  position: "absolute", top: "50%", left: "50%",
                  width: 0, height: 0, zIndex: 2000,
                }}>
                  {/* Pulse ring effect */}
                  <div style={{
                    position: "absolute", top: -20, left: -20,
                    width: 40, height: 40, borderRadius: "50%",
                    border: `1px solid ${GOLD}40`,
                    animation: "ringPulse 1.5s ease-out infinite",
                  }} />
                  <div style={{
                    position: "absolute", top: -20, left: -20,
                    width: 40, height: 40, borderRadius: "50%",
                    border: `1px solid ${GOLD}30`,
                    animation: "ringPulse 1.5s ease-out infinite .5s",
                  }} />

                  {/* Flag buttons scattered around globe */}
                  {languages.map((lang, i) => {
                    const isActive = currentLang === lang.code;
                    const delay = i * 0.04;
                    return (
                      <button
                        key={lang.code}
                        onClick={() => handleLangSelect(lang.code)}
                        title={lang.label}
                        style={{
                          position: "absolute",
                          left: lang.x, top: lang.y,
                          width: isActive ? 40 : 34, height: isActive ? 40 : 34,
                          borderRadius: "50%",
                          border: isActive ? `2px solid ${GOLD}` : `1.5px solid ${IVORY}30`,
                          background: isActive ? `${GOLD}25` : `${BG}dd`,
                          backdropFilter: "blur(8px)",
                          cursor: "pointer",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: isActive ? 20 : 17,
                          boxShadow: isActive
                            ? `0 0 16px ${GOLD}44, 0 4px 12px rgba(0,0,0,.4)`
                            : "0 4px 12px rgba(0,0,0,.5)",
                          transform: "scale(1)",
                          opacity: 1,
                          animation: `flagPop .35s cubic-bezier(.34,1.56,.64,1) ${delay}s both, flagFloat 3s ease ${delay + 1}s infinite`,
                          transition: "border-color .2s, transform .2s, width .2s, height .2s",
                          zIndex: isActive ? 10 : 1,
                        }}
                        onMouseEnter={e => {
                          e.currentTarget.style.transform = "scale(1.25)";
                          e.currentTarget.style.borderColor = GOLD;
                          e.currentTarget.style.zIndex = 20;
                        }}
                        onMouseLeave={e => {
                          e.currentTarget.style.transform = "scale(1)";
                          e.currentTarget.style.borderColor = isActive ? GOLD : `${IVORY}30`;
                          e.currentTarget.style.zIndex = isActive ? 10 : 1;
                        }}
                      >
                        {flagCircle(lang, isActive ? 24 : 20)}
                      </button>
                    );
                  })}

                  {/* Tooltip for hovered / current language */}
                  <div style={{
                    position: "absolute", top: 110, left: "50%", transform: "translateX(-50%)",
                    ...S.sf, fontSize: 10, fontWeight: 500, letterSpacing: 2,
                    color: GOLD, textTransform: "uppercase", whiteSpace: "nowrap",
                    padding: "6px 14px", background: `${BG}ee`, border: `1px solid ${GOLD}30`,
                    borderRadius: 4, animation: "slideUp .4s ease .3s both",
                  }}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      {flagCircle(languages.find(l => l.code === currentLang), 14)}
                      {languages.find(l => l.code === currentLang)?.label}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </nav>

          {/* Mobile hamburger */}
          <button
            id="mobile-hamburger"
            onClick={() => setMobileOpen(!mobileOpen)}
            style={{ background: "none", border: "1px solid " + GOLD + "60", color: GOLD, fontSize: 24, cursor: "pointer", padding: "8px 12px", lineHeight: 1, zIndex: 10001, position: "relative" }}
          >
            {mobileOpen ? "✕" : "☰"}
          </button>
        </div>
      </header>

      {/* ═══════════ 2. HERO SECTION ═══════════ */}
      <section style={{ position: "relative", height: "100vh", overflow: "hidden" }}>
        {/* Background layers */}
        {heroSlides.map((slide, i) => (
          <div key={i} style={{
            position: "absolute", inset: 0,
            opacity: heroIdx === i ? 1 : 0,
            transition: "opacity 1.5s ease",
          }}>
            <img width={slide.w} height={slide.h} src={slide.img} alt="WOCS 프리미엄 글램핑 시공 index" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} />
            <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(9,9,11,0) 0%, rgba(9,9,11,0) 50%, rgba(9,9,11,0) 100%)" }} />
          </div>
        ))}

        {/* Geometric decorations */}
        <div style={{ position: "absolute", top: "15%", right: "10%", width: 300, height: 300, border: `1px solid ${GOLD}12`, transform: `rotate(${45 + scrollY * 0.02}deg)`, transition: "transform 0.1s" }} />
        <div style={{ position: "absolute", bottom: "20%", left: "8%", width: 200, height: 200, borderRadius: "50%", border: `1px solid ${GOLD}08`, animation: "rotate 40s linear infinite" }} />
        <div style={{ position: "absolute", top: "40%", right: "25%", width: 4, height: 4, background: GOLD, borderRadius: "50%", animation: "pulse 3s ease infinite", boxShadow: `0 0 20px ${GOLD}44` }} />

        {/* Geodesic wireframe SVG */}
        <svg style={{ position: "absolute", right: "-5%", top: "10%", width: "55%", height: "80%", opacity: 0.04 }} viewBox="0 0 500 500">
          <g stroke={GOLD} strokeWidth="0.5" fill="none">
            <polygon points="250,50 450,180 400,380 100,380 50,180" />
            <polygon points="250,50 350,130 350,280 150,280 150,130" />
            <line x1="250" y1="50" x2="250" y2="280" />
            <line x1="50" y1="180" x2="350" y2="130" />
            <line x1="450" y1="180" x2="150" y2="130" />
            <line x1="100" y1="380" x2="350" y2="280" />
            <line x1="400" y1="380" x2="150" y2="280" />
            <circle cx="250" cy="200" r="120" />
            <circle cx="250" cy="200" r="180" />
          </g>
        </svg>

        {/* Hero content */}
        <div style={{ position: "relative", zIndex: 10, height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 8%", maxWidth: 900 }}>
          {/* Slide tag */}
          <div key={`tag-${heroIdx}`} style={{
            ...S.sf, ...S.slab, marginBottom: 24,
            animation: "slideUp .6s ease forwards",
          }}>
            {heroSlides[heroIdx].tag}
          </div>

          {/* Title */}
          <h2 key={`title-${heroIdx}`} style={{
            fontSize: "clamp(48px, 7vw, 96px)", fontWeight: 300, lineHeight: 1.05,
            letterSpacing: -1, whiteSpace: "pre-line", marginBottom: 24,
            animation: "slideUp .8s ease forwards",
          }}>
            {heroSlides[heroIdx].title}
          </h2>

          {/* Subtitle */}
          <p key={`sub-${heroIdx}`} style={{
            ...S.sf, fontSize: 16, fontWeight: 300, color: `${IVORY}99`, maxWidth: 500,
            lineHeight: 1.7, marginBottom: 40,
            animation: "slideUp 1s ease forwards",
          }}>
            {heroSlides[heroIdx].sub}
          </p>

          {/* CTA buttons */}
          <div key={`cta-${heroIdx}`} style={{
            display: "flex", gap: 16, animation: "slideUp 1.1s ease forwards",
          }}>
            <a href={heroSlides[heroIdx].href+"?lang="+currentLang} className="btn-gold-fill" style={{textDecoration:"none"}}>{heroSlides[heroIdx].cta}</a>
            <a href={"contact/index.html?lang="+currentLang} className="btn-gold" style={{textDecoration:"none"}}>{t("contactUs")}</a>
          </div>

          {/* Slide indicators */}
          <div style={{ display: "flex", gap: 12, marginTop: 60 }}>
            {heroSlides.map((_, i) => (
              <button key={i} onClick={() => setHeroIdx(i)} style={{
                width: heroIdx === i ? 40 : 20, height: 3,
                background: heroIdx === i ? GOLD : `${IVORY}30`,
                border: "none", cursor: "pointer", transition: "all .4s",
              }} />
            ))}
          </div>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: "absolute", bottom: 40, left: "50%", transform: "translateX(-50%)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
          animation: "float 3s ease infinite",
        }}>
          <div style={{ ...S.sf, fontSize: 9, letterSpacing: 4, color: `${IVORY}55` }}>{t("scroll")}</div>
          <div style={{ width: 1, height: 40, background: `linear-gradient(to bottom, ${GOLD}66, transparent)` }} />
        </div>
      </section>

      {/* ═══════════ 3. PRODUCT GRID (Glitzcamp Style) ═══════════ */}
      <section id="products" style={{ background: BG2, padding: "100px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }} {...anim("pg-title")}>
            <div style={S.slab}>{t("ourProducts")}</div>
            <h2 style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 300, marginTop: 12 }}>
              {t("premiumCollection").replace(t("premiumW"), "").replace(/\s+/g, " ").trim()} <span className="gold-text">{t("premiumW")}</span>
            </h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 24 }}>
            {productCards.map((card, i) => (
              <div key={i} {...anim(`pc-${i}`, "fu", i * 0.12)} style={{
                ...anim(`pc-${i}`, "fu", i * 0.12).style,
                background: BG3, border: `1px solid ${GOLD}15`, padding: 0,
                cursor: "pointer", transition: "all .5s", position: "relative", overflow: "hidden",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = `${GOLD}55`; e.currentTarget.style.transform = "translateY(-8px)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = `${GOLD}15`; e.currentTarget.style.transform = "none"; }}
              onClick={() => window.location.href=card.href+"?lang="+currentLang}
              >
                {/* Card image area */}
                <div style={{ height: 200, overflow: "hidden" }}>
                  <img width={card.w} height={card.h} src={card.img} alt={card.name} style={{width:"100%",height:"100%",objectFit:"cover"}} />
                </div>
                {/* Card info */}
                <div style={{ padding: "24px 28px 28px" }}>
                  <div style={{ ...S.sf, fontSize: 14, fontWeight: 600, letterSpacing: 2, color: IVORY }}>{card.name}</div>
                  <div style={{ ...S.sf, fontSize: 12, color: `${IVORY}55`, marginTop: 8 }}>{card.sub}</div>
                  <div style={{ ...S.sf, fontSize: 11, color: GOLD, marginTop: 16, letterSpacing: 2, fontWeight: 500 }}>{t("explore")}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 4. WOCS ADVANTAGE (Luna Style) ═══════════ */}
      <section id="advantage" style={{ background: BG, padding: "120px 5%", position: "relative" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "center" }}>
          {/* Left text */}
          <div {...anim("adv-txt", "fr")}>
            <div style={S.slab}>{t("advTag")}</div>
            <h2 style={{ fontSize: "clamp(36px, 4vw, 56px)", fontWeight: 300, lineHeight: 1.15, marginTop: 16 }}>
              {t("advTitle1")}<br /><span className="shimmer-text">{t("advTitle2")}</span>
            </h2>
            <p style={{ ...S.sf, fontSize: 15, lineHeight: 1.9, color: `${IVORY}88`, marginTop: 28 }}>
              {t("advP1")}
            </p>
            <p style={{ ...S.sf, fontSize: 15, lineHeight: 1.9, color: `${IVORY}88`, marginTop: 16 }}>
              {t("advP2")}
            </p>

            {/* Badges (Luna Style) */}
            <div style={{ display: "flex", gap: 16, marginTop: 40, flexWrap: "wrap" }}>
              {badges.map((b, i) => (
                <div key={i} style={{
                  display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
                  padding: "16px 18px", border: `1px solid ${GOLD}20`, background: `${BG2}`,
                  minWidth: 80, transition: "all .3s", cursor: "default",
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = `${GOLD}66`}
                onMouseLeave={e => e.currentTarget.style.borderColor = `${GOLD}20`}
                >
                  <span style={{ fontSize: 22 }}>{b.icon}</span>
                  <span style={{ ...S.sf, fontSize: 10, letterSpacing: 2, color: `${IVORY}99`, textTransform: "uppercase" }}>{b.label}</span>
                </div>
              ))}
            </div>

            <a href={"about/technology.html?lang="+currentLang} className="btn-gold" style={{marginTop:40,textDecoration:"none",display:"inline-block"}}>{t("learnMore")}</a>
          </div>

          {/* Right - Geodesic SVG */}
          <div {...anim("adv-svg", "fs")} style={{
            ...anim("adv-svg", "fs").style,
            display: "flex", alignItems: "center", justifyContent: "center", position: "relative",
          }}>
            <svg viewBox="0 0 400 400" style={{ width: "100%", maxWidth: 420 }}>
              <defs>
                <linearGradient id="geoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor={GOLD} stopOpacity="0.5" />
                  <stop offset="100%" stopColor={GOLD} stopOpacity="0.1" />
                </linearGradient>
              </defs>
              <g stroke="url(#geoGrad)" strokeWidth="0.8" fill="none">
                {/* Geodesic dome wireframe */}
                <circle cx="200" cy="200" r="160" strokeOpacity="0.15" />
                <circle cx="200" cy="200" r="120" strokeOpacity="0.2" />
                <circle cx="200" cy="200" r="80" strokeOpacity="0.25" />
                {/* Triangular framework */}
                <polygon points="200,40 360,200 320,340 80,340 40,200" strokeOpacity="0.3" />
                <polygon points="200,80 320,200 280,300 120,300 80,200" strokeOpacity="0.35" />
                <polygon points="200,120 280,200 250,260 150,260 120,200" strokeOpacity="0.4" />
                {/* Cross lines */}
                <line x1="200" y1="40" x2="200" y2="340" strokeOpacity="0.12" />
                <line x1="40" y1="200" x2="360" y2="200" strokeOpacity="0.12" />
                <line x1="80" y1="340" x2="320" y2="340" strokeOpacity="0.12" />
                {/* Radial lines */}
                <line x1="200" y1="40" x2="80" y2="340" strokeOpacity="0.1" />
                <line x1="200" y1="40" x2="320" y2="340" strokeOpacity="0.1" />
                <line x1="40" y1="200" x2="320" y2="340" strokeOpacity="0.1" />
                <line x1="360" y1="200" x2="80" y2="340" strokeOpacity="0.1" />
                {/* Vertex dots */}
                {[[200,40],[360,200],[320,340],[80,340],[40,200],[200,80],[320,200],[280,300],[120,300],[80,200],[200,120],[280,200],[250,260],[150,260],[120,200]].map(([cx,cy], i) => (
                  <circle key={i} cx={cx} cy={cy} r="3" fill={GOLD} fillOpacity="0.5" />
                ))}
              </g>
              {/* Center text */}
              <text x="200" y="195" textAnchor="middle" fill={GOLD} fontFamily="Cormorant Garamond" fontSize="28" fontWeight="300" opacity="0.7">WOCS</text>
              <text x="200" y="218" textAnchor="middle" fill={GOLD} fontFamily="Lexend" fontSize="8" letterSpacing="4" opacity="0.5">PATENTED TECHNOLOGY</text>
            </svg>
          </div>
        </div>
      </section>

      {/* ═══════════ 5. MARQUEE BANNER (Luna Style) ═══════════ */}
      <div style={{ background: GOLD, padding: "14px 0", overflow: "hidden" }}>
        <div style={{ display: "flex", animation: "marquee 25s linear infinite", whiteSpace: "nowrap" }}>
          {[...Array(2)].map((_, ri) => (
            <div key={ri} style={{ display: "flex", gap: 0 }}>
              {[t("marq1"), t("marq2"), t("marq3"), t("marq4"), t("marq5"), t("marq6"), t("marq7")].map((txt, i) => (
                <span key={i} style={{ ...S.sf, fontSize: 12, fontWeight: 500, letterSpacing: 3, color: BG, padding: "0 40px", textTransform: "uppercase" }}>
                  ◆ {txt}
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* ═══════════ 6. DOME SIZE SELECTOR (Luna Style) ═══════════ */}
      <section id="domes" style={{ background: BG2, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 60 }} {...anim("dome-title")}>
            <div style={S.slab}>{t("domeTag")}</div>
            <h2 style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 300, marginTop: 12 }}>
              {t("chooseSize").split(" ").slice(0, -1).join(" ")} <span className="gold-text">{t("chooseSize").split(" ").pop()}</span>
            </h2>
          </div>

          {/* Size tabs */}
          <div style={{ display: "flex", justifyContent: "center", gap: 8, marginBottom: 48 }} {...anim("dome-tabs")}>
            {domeSizes.map((d, i) => (
              <button key={i} onClick={() => setActiveDome(i)} style={{
                ...S.sf, fontSize: 14, fontWeight: activeDome === i ? 600 : 300,
                padding: "14px 24px", cursor: "pointer", transition: "all .4s",
                background: activeDome === i ? GOLD : "transparent",
                color: activeDome === i ? BG : `${IVORY}88`,
                border: `1px solid ${activeDome === i ? GOLD : `${GOLD}30`}`,
              }}>
                {d.s}
              </button>
            ))}
          </div>

          {/* Selected dome info */}
          <div key={activeDome} style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, alignItems: "center",
            animation: "slideUp .5s ease",
          }}>
            {/* Dome visual */}
            <div style={{
              aspectRatio: "4/3", overflow: "hidden", position: "relative",
              border: `1px solid ${GOLD}15`, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", position: "relative",
            }}>
              {/* Dome illustration */}
              <svg viewBox="0 0 300 200" style={{ width: "80%", opacity: 0.6 }}>
                <defs>
                  <linearGradient id="domeG" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor={GOLD} stopOpacity="0.6" />
                    <stop offset="100%" stopColor={GOLD} stopOpacity="0.05" />
                  </linearGradient>
                </defs>
                <ellipse cx="150" cy="160" rx="130" ry="15" fill={GOLD} fillOpacity="0.1" />
                <path d={`M 20 160 Q 20 ${50 - activeDome * 2} 150 ${30 - activeDome * 1.5} Q 280 ${50 - activeDome * 2} 280 160`} stroke={GOLD} strokeWidth="1.5" fill="url(#domeG)" fillOpacity="0.15" />
                {/* Triangle grid lines */}
                {[0.25, 0.5, 0.75].map((t, i) => (
                  <ellipse key={i} cx="150" cy={160 - (130 - activeDome * 3) * t} rx={130 * (1 - t * 0.8)} ry={8 * (1 - t * 0.5)} stroke={GOLD} strokeWidth="0.5" fill="none" strokeOpacity="0.3" />
                ))}
                {[60, 100, 150, 200, 240].map((x, i) => (
                  <line key={i} x1={x} y1="160" x2="150" y2={30 - activeDome * 1.5} stroke={GOLD} strokeWidth="0.3" strokeOpacity="0.2" />
                ))}
              </svg>
              <div style={{ ...S.sf, fontSize: 80, fontWeight: 200, color: GOLD, position: "absolute", opacity: 0.1 }}>{domeSizes[activeDome].s}</div>
            </div>

            {/* Dome details */}
            <div>
              <div style={{ fontSize: "clamp(40px, 5vw, 72px)", fontWeight: 300, lineHeight: 1 }}>
                <span className="gold-text">{domeSizes[activeDome].s}</span>
              </div>
              <div style={{ ...S.sf, fontSize: 13, color: `${IVORY}66`, marginTop: 12, letterSpacing: 1 }}>{t("geoLabel")}</div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginTop: 36 }}>
                {[
                  { label: t("area"), value: domeSizes[activeDome].area },
                  { label: t("capacity"), value: domeSizes[activeDome].people },
                  { label: t("priceRange"), value: domeSizes[activeDome].price },
                  { label: t("fourSeason"), value: t("possible") },
                ].map((item, i) => (
                  <div key={i} style={{ padding: "20px 0", borderBottom: `1px solid ${GOLD}15` }}>
                    <div style={{ ...S.sf, fontSize: 10, letterSpacing: 3, color: GOLD, textTransform: "uppercase", marginBottom: 6 }}>{item.label}</div>
                    <div style={{ ...S.sf, fontSize: 20, fontWeight: 300, color: IVORY }}>{item.value}</div>
                  </div>
                ))}
              </div>

              <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}88`, lineHeight: 1.8, marginTop: 24 }}>
                {domeSizes[activeDome].desc}
              </p>

              <div style={{ display: "flex", gap: 16, marginTop: 36 }}>
                <a href={"products/geodesic-domes.html?lang="+currentLang} className="btn-gold-fill" style={{textDecoration:"none"}}>{t("buildDome")}</a>
                <a href={"products/geodesic-domes.html?lang="+currentLang+"#sizes"} className="btn-gold" style={{textDecoration:"none"}}>{t("detailSpec")}</a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ 7. PRODUCT SHOWCASE SECTIONS (Luna Style) ═══════════ */}
      {productSections.map((prod, pi) => (
        <section key={pi} style={{ background: pi % 2 === 0 ? BG : BG2, padding: "120px 5%" }}>
          <div style={{ maxWidth: 1400, margin: "0 auto", display: "grid", gridTemplateColumns: pi % 2 === 0 ? "1fr 1fr" : "1fr 1fr", gap: 80, alignItems: "center" }}>
            {/* Text side */}
            <div style={{ order: pi % 2 === 0 ? 1 : 2 }} {...anim(`prod-${pi}`, pi % 2 === 0 ? "fr" : "fl")}>
              <div style={{ ...S.sf, fontSize: 10, letterSpacing: 4, color: GOLD, marginBottom: 12 }}>{prod.tag}</div>

              {/* Tab-like tags */}
              <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
                {prod.tag.split(" · ").map((tagItem, ti) => (
                  <span key={ti} style={{ ...S.sf, fontSize: 10, fontWeight: 500, letterSpacing: 2, color: GOLD, padding: "4px 12px", border: `1px solid ${GOLD}30`, textTransform: "uppercase" }}>
                    {tagItem}
                  </span>
                ))}
              </div>

              <h3 style={{ fontSize: "clamp(28px, 3.5vw, 44px)", fontWeight: 300, marginTop: 20, lineHeight: 1.2 }}>
                {prod.label}
              </h3>

              <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}88`, lineHeight: 1.9, marginTop: 24 }}>{prod.desc}</p>

              {/* Feature list */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 28 }}>
                {prod.features.map((f, fi) => (
                  <div key={fi} style={{ ...S.sf, fontSize: 13, color: `${IVORY}bb`, display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ color: GOLD, fontSize: 14 }}>◆</span> {f}
                  </div>
                ))}
              </div>

              <a href={"products/" + (pi===0?"geodesic-domes.html":pi===1?"safari-tents.html":pi===2?"luxury-tents.html":"bell-tent.html")} className="btn-gold" style={{marginTop:36,textDecoration:"none",display:"inline-block"}}>{prod.cta}</a>
            </div>

            {/* Visual side */}
            <div style={{ order: pi % 2 === 0 ? 2 : 1 }} {...anim(`prodv-${pi}`, "fs")}>
              <div style={{aspectRatio:"4/3",overflow:"hidden",border:`1px solid ${GOLD}12`}}>
                <img src={pi === 0 ? "assets/images/19-d800-ext.webp" : pi === 1 ? "assets/images/15-lodge-lx-ext.webp" : pi === 2 ? "assets/images/22-sig-o-ext.webp" : "assets/images/37-sig-m-s60-ext.webp"} alt={prod.label} style={{width:"100%",height:"100%",objectFit:"cover"}} />
              </div>
            </div>
          </div>
        </section>
      ))}

      {/* ═══════════ 8. OCCASIONS GRID (Glitzcamp Style) ═══════════ */}
      <section id="occasions" style={{ background: BG2, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }} {...anim("occ-title")}>
            <div style={S.slab}>{t("discoverBuild")}</div>
            <h2 style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 300, marginTop: 12 }}>
              {t("forEvery")} <span className="gold-text">{t("occasionW")}</span>
            </h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 20 }}>
            {occasions.map((occ, i) => (
              <div key={i}
                {...anim(`occ-${i}`, "fu", i * 0.06)}
                onMouseEnter={() => setHovOccasion(i)}
                onMouseLeave={() => setHovOccasion(null)}
                onClick={() => window.location.href=occ.href+"?lang="+currentLang}
                style={{
                  ...anim(`occ-${i}`, "fu", i * 0.06).style,
                  padding: "36px 20px", textAlign: "center", cursor: "pointer",
                  background: hovOccasion === i ? `${GOLD}12` : "transparent",
                  border: `1px solid ${hovOccasion === i ? `${GOLD}44` : `${GOLD}10`}`,
                  transition: "all .4s",
                  transform: `${anim(`occ-${i}`, "fu", i * 0.06).style.transform} ${hovOccasion === i ? "translateY(-6px)" : ""}`,
                }}
              >
                <div style={{ marginBottom: 14, transition: "transform .3s", transform: hovOccasion === i ? "scale(1.1)" : "scale(1)" }}><img width={occ.w} height={occ.h} src={occ.img} alt={occ.name} style={{width:"80px",height:"80px",objectFit:"cover",borderRadius:"8px"}} /></div>
                <div style={{ ...S.sf, fontSize: 13, fontWeight: 500, color: IVORY }}>{occ.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 9. PROJECT CASES (Glitzcamp Style) ═══════════ */}
      <section id="cases" style={{ background: BG, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 60 }}>
            {/* Left header */}
            <div {...anim("case-head", "fr")}>
              <div style={S.slab}>{t("caseTag")}</div>
              <h2 style={{ fontSize: "clamp(32px, 3.5vw, 48px)", fontWeight: 300, marginTop: 12, lineHeight: 1.2 }}>
                {t("globalPortfolio")}
              </h2>
              <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}77`, lineHeight: 1.8, marginTop: 20 }}>
                {t("caseP")}
              </p>
              <a href={"portfolio/index.html?lang="+currentLang} className="btn-gold" style={{marginTop:32,textDecoration:"none",display:"inline-block"}}>{t("viewAllCases")}</a>
            </div>

            {/* Right case cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              {cases.map((c, i) => (
                <div key={i}
                  {...anim(`case-${i}`, "fu", i * 0.1)}
                  onMouseEnter={() => setActiveCase(i)}
                  onClick={() => window.location.href=c.href+"?lang="+currentLang}
                  style={{
                    ...anim(`case-${i}`, "fu", i * 0.1).style,
                    padding: 28, background: activeCase === i ? `${GOLD}0c` : BG2,
                    border: `1px solid ${activeCase === i ? `${GOLD}40` : `${GOLD}10`}`,
                    cursor: "pointer", transition: "all .4s",
                  }}
                >
                  <div style={{ ...S.sf, fontSize: 11, color: GOLD, letterSpacing: 2, marginBottom: 10 }}>{c.country}</div>
                  <div style={{ fontSize: 22, fontWeight: 400, marginBottom: 8 }}>{c.name}</div>
                  <div style={{ ...S.sf, fontSize: 13, color: `${IVORY}77`, lineHeight: 1.6 }}>{c.desc}</div>
                  <div style={{ ...S.sf, fontSize: 11, color: GOLD, marginTop: 16, letterSpacing: 2, fontWeight: 500 }}>{t("readMore")}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ 10. EIGHT-STEP PROCESS (Glitzcamp Style) ═══════════ */}
      <section id="project" style={{ background: BG2, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 72 }} {...anim("step-title")}>
            <div style={S.slab}>{t("stepTag")}</div>
            <h2 style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 300, marginTop: 12 }}>
              {t("stepTitle")} <span className="gold-text">{t("sixSteps")}</span>
            </h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
            {steps.map((step, i) => (
              <div key={i}
                {...anim(`step-${i}`, "fu", i * 0.1)}
                onMouseEnter={() => setActiveStep(i)}
                style={{
                  ...anim(`step-${i}`, "fu", i * 0.1).style,
                  padding: "32px 20px", textAlign: "center",
                  background: activeStep === i ? `${GOLD}0c` : "transparent",
                  border: `1px solid ${activeStep === i ? `${GOLD}44` : `${GOLD}10`}`,
                  cursor: "pointer", transition: "all .4s", position: "relative",
                }}
              >
                {/* Step number */}
                <div style={{ marginBottom: 8 }} dangerouslySetInnerHTML={{__html: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="36" height="36" fill="none" stroke="#c9a96e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' + step.svg + '</svg>'}} />
                <div style={{ ...S.sf, fontSize: 32, fontWeight: 200, color: activeStep === i ? GOLD : `${IVORY}22`, transition: "color .4s", marginBottom: 12 }}>
                  {step.n}
                </div>
                <div style={{ ...S.sf, fontSize: 13, fontWeight: 500, color: IVORY, marginBottom: 12 }}>{step.title}</div>
                <div style={{
                  ...S.sf, fontSize: 12, color: `${IVORY}77`, lineHeight: 1.7,
                  maxHeight: activeStep === i ? 200 : 0, overflow: "hidden", transition: "max-height .5s",
                }}>
                  {step.desc}
                </div>
                {/* Connector line */}
                {(i < 7 && i !== 3) && <div style={{ position: "absolute", top: "30%", right: -8, width: 16, height: 1, background: `${GOLD}30` }} />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 11. EXPERIENCE FEATURES (Glitzcamp Style) ═══════════ */}
      <section style={{ background: BG, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }} {...anim("exp-title")}>
            <div style={S.slab}>{t("expTag")}</div>
            <h2 style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 300, marginTop: 12 }}>
              {t("expTitle")} <span className="gold-text">{t("expDiff")}</span>
            </h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 24 }}>
            {features.map((f, i) => (
              <div key={i} {...anim(`feat-${i}`, "fu", i * 0.12)} style={{
                ...anim(`feat-${i}`, "fu", i * 0.12).style,
                padding: 36, border: `1px solid ${GOLD}15`, textAlign: "center",
                background: `linear-gradient(180deg, ${GOLD}05 0%, transparent 100%)`,
                transition: "all .4s",
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = `${GOLD}44`}
              onMouseLeave={e => e.currentTarget.style.borderColor = `${GOLD}15`}
              >
                <div style={{ marginBottom: 20 }} dangerouslySetInnerHTML={{__html: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#c9a96e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' + f.svg + '</svg>'}} />
                <div style={{ ...S.sf, fontSize: 14, fontWeight: 500, color: IVORY, marginBottom: 14 }}>{f.title}</div>
                <div style={{ ...S.sf, fontSize: 13, color: `${IVORY}77`, lineHeight: 1.7 }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 12. STATS (Glitzcamp Style) ═══════════ */}
      <section data-s="stats" style={{ background: `linear-gradient(135deg, ${BG2}, ${BG})`, padding: "100px 5%", borderTop: `1px solid ${GOLD}10`, borderBottom: `1px solid ${GOLD}10` }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 40, textAlign: "center" }}>
          {statsData.map((stat, i) => (
            <div key={i} style={{ padding: "20px 0" }}>
              <div style={{ fontSize: "clamp(48px, 5vw, 72px)", fontWeight: 300, lineHeight: 1 }}>
                <span className="gold-text">{stat.val}</span>
                <span style={{ color: GOLD, fontSize: "0.5em" }}>{stat.suffix}</span>
              </div>
              <div style={{ ...S.sf, fontSize: 12, letterSpacing: 3, color: `${IVORY}66`, marginTop: 12 }}>{stat.ko}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════ 13. B2B OPPORTUNITIES (Luna Style) ═══════════ */}
      <section style={{ background: BG, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "center" }}>
          <div {...anim("b2b-visual", "fs")} style={{
            ...anim("b2b-visual", "fs").style,
            aspectRatio: "1", background: `radial-gradient(circle at 40% 40%, ${GOLD}12, transparent 60%)`,
            border: `1px solid ${GOLD}12`, display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 100, opacity: 0.2 }}>🤝</div>
              <div style={{ ...S.sf, fontSize: 11, letterSpacing: 4, color: GOLD, marginTop: 20 }}>{t("b2bAlliance")}</div>
            </div>
          </div>

          <div {...anim("b2b-txt", "fl")}>
            <div style={S.slab}>{t("b2bTag")}</div>
            <h2 style={{ fontSize: "clamp(32px, 3.5vw, 48px)", fontWeight: 300, marginTop: 12, lineHeight: 1.2 }}>
              B2B <span className="gold-text">{t("b2bTitle").replace("B2B ", "")}</span>
            </h2>
            <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}88`, lineHeight: 1.9, marginTop: 24 }}>
              {t("b2bP1")}
            </p>
            <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}88`, lineHeight: 1.9, marginTop: 16 }}>
              {t("b2bP2")}
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 32 }}>
              {[
                { label: t("b2bItem1"), desc: t("b2bItem1d"), href: "project/financing.html" },
                { label: t("b2bItem2"), desc: t("b2bItem2d"), href: "project/revenue-sharing.html" },
                { label: t("b2bItem3"), desc: t("b2bItem3d"), href: "project/bulk-order.html" },
                { label: t("b2bItem4"), desc: t("b2bItem4d"), href: "contact/roi-calculator.html" },
              ].map((item, i) => (
                <div key={i} style={{ padding: "16px 20px", border: `1px solid ${GOLD}15`, cursor: "pointer", transition: "all .3s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = `${GOLD}55`}
                  onMouseLeave={e => e.currentTarget.style.borderColor = `${GOLD}15`}
                  onClick={() => window.location.href=item.href+"?lang="+currentLang}
                >
                  <div style={{ ...S.sf, fontSize: 13, fontWeight: 500, color: GOLD }}>{item.label}</div>
                  <div style={{ ...S.sf, fontSize: 12, color: `${IVORY}66`, marginTop: 4 }}>{item.desc}</div>
                </div>
              ))}
            </div>

            <a href={"contact/quote.html?lang="+currentLang} className="btn-gold" style={{marginTop:36,textDecoration:"none",display:"inline-block"}}>{t("b2bExplore")}</a>
          </div>
        </div>
      </section>

      {/* ═══════════ 14. REVIEWS (Both Styles) ═══════════ */}
      <section id="gallery" style={{ background: BG2, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto", textAlign: "center" }}>
          <div style={S.slab}>{t("reviewTag")}</div>
          <h2 style={{ fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 300, marginTop: 12, marginBottom: 60 }}>
            {t("reviewTitle")}
          </h2>

          {/* Review card */}
          <div key={activeReview} style={{
            padding: "48px 60px", border: `1px solid ${GOLD}20`,
            background: `linear-gradient(135deg, ${GOLD}05, transparent)`,
            animation: "slideUp .6s ease",
          }}>
            {/* Stars */}
            <div style={{ fontSize: 18, letterSpacing: 4, color: GOLD, marginBottom: 24 }}>
              {"★".repeat(reviews[activeReview].stars)}
            </div>
            <p style={{ fontSize: 20, fontWeight: 300, fontStyle: "italic", lineHeight: 1.8, color: `${IVORY}cc`, marginBottom: 32 }}>
              "{reviews[activeReview].text}"
            </p>
            <div style={{ ...S.sf, fontSize: 14, fontWeight: 500, color: IVORY }}>{reviews[activeReview].name}</div>
            <div style={{ ...S.sf, fontSize: 12, color: `${IVORY}55`, marginTop: 4 }}>{reviews[activeReview].loc}</div>
          </div>

          {/* Review indicators */}
          <div style={{ display: "flex", justifyContent: "center", gap: 10, marginTop: 32 }}>
            {reviews.map((_, i) => (
              <button key={i} onClick={() => setActiveReview(i)} style={{
                width: 10, height: 10, borderRadius: "50%",
                background: activeReview === i ? GOLD : `${IVORY}22`,
                border: "none", cursor: "pointer", transition: "all .3s",
              }} />
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 15. BLOG SECTION (Glitzcamp Style) ═══════════ */}
      <section id="resources" style={{ background: BG, padding: "120px 5%" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 48 }}>
            <div {...anim("blog-head")}>
              <div style={S.slab}>{t("blogTag")}</div>
              <h2 style={{ fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 300, marginTop: 12 }}>
                {t("blogTitle")}
              </h2>
            </div>
            <a href={"resources/blog.html?lang="+currentLang} className="btn-gold" style={{padding:"10px 24px",textDecoration:"none"}}>{t("viewAll")}</a>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
            {blogs.map((blog, i) => (
              <div key={i} {...anim(`blog-${i}`, "fu", i * 0.12)} style={{
                ...anim(`blog-${i}`, "fu", i * 0.12).style,
                border: `1px solid ${GOLD}12`, cursor: "pointer", transition: "all .4s", overflow: "hidden",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = `${GOLD}44`; e.currentTarget.style.transform = "translateY(-4px)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = `${GOLD}12`; e.currentTarget.style.transform = "none"; }}
              onClick={() => window.location.href=blog.href+"?lang="+currentLang}
              >
                <div style={{ height: 200, position: "relative", overflow: "hidden" }}>
                  <img width={blog.w} height={blog.h} src={blog.img} alt={blog.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} loading="lazy" />
                  <span style={{ ...S.sf, fontSize: 10, letterSpacing: 3, color: GOLD, padding: "6px 16px", border: `1px solid ${GOLD}40`, position: "absolute", top: 16, left: 16, background: "rgba(9,9,11,0.7)" }}>{blog.tag}</span>
                </div>
                <div style={{ padding: "24px 28px" }}>
                  <h4 style={{ fontSize: 18, fontWeight: 400, lineHeight: 1.4, marginBottom: 6 }}>{blog.title}</h4>
                  <div style={{ ...S.sf, fontSize: 13, color: `${IVORY}55` }}>{blog.ko}</div>
                  <div style={{ ...S.sf, fontSize: 11, color: GOLD, marginTop: 16, letterSpacing: 2 }}>{t("readMore")}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ 15.5 WOCS 소개 (ABOUT) ═══════════ */}
      <section id="about" style={{ background: `linear-gradient(180deg, ${BG}, ${BG2})`, padding: "120px 5%", borderTop: `1px solid ${GOLD}15` }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }} {...anim("about")}>
          <div style={S.slab}>{currentLang === "ko" ? "WOCS 소개" : "ABOUT WOCS"}</div>
          <h2 style={{ fontSize: "clamp(32px, 4vw, 56px)", fontWeight: 300, marginTop: 16, lineHeight: 1.15 }}>
            {currentLang === "ko" ? "16년 경력의 " : "16+ Years of "}
            <span className="gold-text">{currentLang === "ko" ? "글램핑 전문가" : "Glamping Expertise"}</span>
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 60, marginTop: 60 }}>
            <div>
              <p style={{ ...S.sf, fontSize: 15, color: `${IVORY}bb`, lineHeight: 1.9, marginBottom: 24 }}>
                {currentLang === "ko"
                  ? "WOCS(우성어닝천막공사캠프시스템)는 2009년부터 글램핑·글램핑 시공 분야에서 16년 이상의 경력을 쌓아온 전문 업체입니다. 특허받은 '무용접 다방향 유니버설 조인트' 기술로 업계에서 독보적인 위치를 확보하고 있습니다."
                  : "WOCS (Woosung Awning Tent Camp System) has been a specialist in glamping and tent construction since 2009. Our patented 'Weldless Multi-Directional Universal Joint' technology sets us apart in the industry."}
              </p>
              <p style={{ ...S.sf, fontSize: 15, color: `${IVORY}bb`, lineHeight: 1.9 }}>
                {currentLang === "ko"
                  ? "이중 쐐기 가압 방식(Double-Wedge Pressurization)의 독자적 잠금 구조로, 용접 없이도 견고한 다방향 연결이 가능합니다. 볼트 조립식이라 3일 내 시공이 완료되며, 전문 용접공 없이도 고품질 구조물을 설치할 수 있습니다."
                  : "Our Double-Wedge Pressurization locking mechanism enables robust multi-directional connections without welding. Bolt-assembly design allows 3-day installation without professional welders."}
              </p>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {[
                { icon: "🔧", title: currentLang === "ko" ? "특허 기술" : "Patented Tech", desc: currentLang === "ko" ? "무용접 다방향 유니버설 조인트" : "Weldless Multi-Directional Universal Joint" },
                { icon: "⏱", title: currentLang === "ko" ? "3일 시공" : "3-Day Build", desc: currentLang === "ko" ? "볼트 조립식으로 빠른 시공" : "Fast bolt-assembly construction" },
                { icon: "🏕", title: currentLang === "ko" ? "화순 쇼룸" : "Hwasun Showroom", desc: currentLang === "ko" ? "전남 화순에서 직접 체험" : "Experience in person in Hwasun" },
                { icon: "📞", title: currentLang === "ko" ? "무료 상담" : "Free Consultation", desc: '<a href="tel:01043370582" style="color:inherit;text-decoration:none">010-4337-0582</a>' },
              ].map((item, i) => (
                <div key={i} style={{
                  display: "flex", gap: 16, alignItems: "center",
                  padding: "20px 24px", background: `${BG}88`, border: `1px solid ${GOLD}15`,
                  transition: "border-color .3s",
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = `${GOLD}44`}
                onMouseLeave={e => e.currentTarget.style.borderColor = `${GOLD}15`}
                >
                  <div style={{ fontSize: 28 }}>{item.icon}</div>
                  <div>
                    <div style={{ ...S.sf, fontSize: 13, fontWeight: 500, color: GOLD, letterSpacing: 1 }}>{item.title}</div>
                    <div style={{ ...S.sf, fontSize: 12, color: `${IVORY}88`, marginTop: 4 }}>{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ 16. NEWSLETTER (Luna Style) ═══════════ */}
      <section style={{ background: `linear-gradient(135deg, ${BG2}, ${BG})`, padding: "100px 5%", borderTop: `1px solid ${GOLD}15` }}>
        <div style={{ maxWidth: 600, margin: "0 auto", textAlign: "center" }} {...anim("news")}>
          <div style={S.slab}>{t("newsTag")}</div>
          <h2 style={{ fontSize: "clamp(28px, 3vw, 40px)", fontWeight: 300, marginTop: 12 }}>
            {t("newsTitle")}
          </h2>
          <p style={{ ...S.sf, fontSize: 14, color: `${IVORY}77`, marginTop: 12, lineHeight: 1.7 }}>
            {t("newsP")}
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 32 }}>
            <input
              type="email" placeholder={t("emailPlaceholder")}
              value={emailVal} onChange={e => setEmailVal(e.target.value)}
              style={{
                flex: 1, padding: "16px 20px", background: `${BG}`, border: `1px solid ${GOLD}30`,
                color: IVORY, fontFamily: "'Lexend', sans-serif", fontSize: 13, outline: "none",
              }}
            />
            <button className="btn-gold-fill" style={{ padding: "16px 32px" }}>{t("subscribe")}</button>
          </div>
        </div>
      </section>

      {/* ═══════════ 17. CTA SECTION ═══════════ */}
      <section id="contact" style={{ background: `radial-gradient(ellipse at 50% 50%, ${GOLD}08, ${BG})`, padding: "120px 5%", textAlign: "center" }}>
        <div style={{ maxWidth: 700, margin: "0 auto" }} {...anim("cta")}>
          <div style={S.slab}>{t("ctaTag")}</div>
          <h2 style={{ fontSize: "clamp(36px, 5vw, 64px)", fontWeight: 300, marginTop: 16, lineHeight: 1.15 }}>
            <span className="shimmer-text">{t("ctaTitle")}</span>
          </h2>
          <p style={{ ...S.sf, fontSize: 15, color: `${IVORY}88`, lineHeight: 1.8, marginTop: 24 }}>
            {t("ctaP")}
          </p>
          <div style={{ display: "flex", gap: 16, justifyContent: "center", marginTop: 40 }}>
            <a href={"contact/index.html?lang="+currentLang} className="btn-gold-fill" style={{textDecoration:"none"}}>{t("ctaCta1")}</a>
            <a href={"resources/downloads.html?lang="+currentLang} className="btn-gold" style={{textDecoration:"none"}}>{t("ctaCta2")}</a>
          </div>
        </div>
      </section>

      {/* ═══════════ 18. FOOTER ═══════════ */}
      <footer style={{ background: BG2, borderTop: `1px solid ${GOLD}15`, padding: "80px 5% 40px" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto" }}>
          {/* Footer columns */}
          <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr", gap: 40, marginBottom: 60 }}>
            {/* Brand column */}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
                <div style={{ width: 36, height: 36, border: `2px solid ${GOLD}`, transform: "rotate(45deg)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ transform: "rotate(-45deg)", fontWeight: 700, fontSize: 16, color: GOLD }}>W</span>
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 18, letterSpacing: 4, color: IVORY }}>WOCS</div>
                  <div style={{ ...S.sf, fontSize: 7, letterSpacing: 3, color: GOLD }}>MODULAR STRUCTURES</div>
                </div>
              </div>
              <p style={{ ...S.sf, fontSize: 12, color: `${IVORY}66`, lineHeight: 1.8, marginBottom: 20 }}>
                {t("footDesc")}
              </p>
              <div style={{ ...S.sf, fontSize: 12, color: `${IVORY}88` }}>
                <div style={{ marginBottom: 6 }}><a href="tel:01043370582" style={{color:'inherit',textDecoration:'none'}}>✆ 010-4337-0582</a></div>
                <div>✉ <a href="mailto:info@wocs.kr" style={{color:'inherit',textDecoration:'none'}}>info@wocs.kr</a></div>
              </div>
            </div>

            {/* Products */}
            <div>
              <div style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 20, textTransform: "uppercase" }}>{t("footProducts")}</div>
              <a href={"products/geodesic-domes.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd1")}</a>
              <a href={"products/safari-tents.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd2")}</a>
              <a href={"products/bell-tent.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd3")}</a>
              <a href={"products/luxury-tents.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd4")}</a>
              <a href={"products/addons.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd5")}</a>
              <a href={"products/geodesic-domes-ready.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd6")}</a>
              <a href={"contact/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footProd7")}</a>

            </div>

            {/* Company */}
            <div>
              <div style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 20, textTransform: "uppercase" }}>{t("footCompany")}</div>
              <a href={"about/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp1")}</a>
              <a href={"resources/blog.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp2")}</a>
              <a href={"resources/reviews.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp3")}</a>
              <a href={"gallery/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp4")}</a>
              <a href={"portfolio/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp5")}</a>
              <a href={"resources/downloads.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp6")}</a>
              <a href={"contact/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footComp7")}</a>

            </div>

            {/* Partners */}
            <div>
              <div style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 20, textTransform: "uppercase" }}>{t("footPartners")}</div>
              <a href={"project/financing.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart1")}</a>
              <a href={"project/revenue-sharing.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart2")}</a>
              <a href={"contact/index.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart3")}</a>
              <a href={"contact/roi-calculator.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart4")}</a>
              <a href={"resources/dealer.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart5")}</a>
              <a href={"resources/downloads.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart6")}</a>
              <a href={"resources/faq.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footPart7")}</a>

            </div>

            {/* Legal */}
            <div>
              <div style={{ ...S.sf, fontSize: 11, fontWeight: 600, letterSpacing: 3, color: GOLD, marginBottom: 20, textTransform: "uppercase" }}>{t("footLegal")}</div>
              <a href={"legal/terms.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footLeg1")}</a>
              <a href={"legal/privacy.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footLeg2")}</a>
              <a href={"resources/downloads.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footLeg3")}</a>
              <a href={"legal/cookies.html?lang="+currentLang} style={{ ...S.sf, fontSize: 12, color: `${IVORY}77`, padding: "6px 0", cursor: "pointer", transition: "color .2s", display: "block", textDecoration: "none" }} onMouseEnter={e => e.target.style.color = GOLD} onMouseLeave={e => e.target.style.color = `${IVORY}77`}>{t("footLeg4")}</a>

            </div>
          </div>

          {/* Divider */}
          <div style={{ height: 1, background: `${GOLD}15`, marginBottom: 30 }} />

          {/* Bottom bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ ...S.sf, fontSize: 11, color: `${IVORY}44` }}>
              {t("footCopy")}
            </div>
            <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
              {[
                {href:"https://instagram.com/woosung_tent",label:"Instagram",d:"M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 01-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 017.8 2zm8.2 2H8A4 4 0 004 8v8a4 4 0 004 4h8a4 4 0 004-4V8a4 4 0 00-4-4zm-4 3.5A4.5 4.5 0 1116.5 12 4.5 4.5 0 0112 7.5zm0 2A2.5 2.5 0 1014.5 12 2.5 2.5 0 0012 9.5zM17 6.5a1 1 0 110 2 1 1 0 010-2z"},
                {href:"https://youtube.com/@countrydiy",label:"YouTube",d:"M22.5 7.5a2.8 2.8 0 00-2-2C18.9 5 12 5 12 5s-6.9 0-8.5.5a2.8 2.8 0 00-2 2A29 29 0 001 12a29 29 0 00.5 4.5 2.8 2.8 0 002 2c1.6.5 8.5.5 8.5.5s6.9 0 8.5-.5a2.8 2.8 0 002-2A29 29 0 0023 12a29 29 0 00-.5-4.5zM10 15V9l5.2 3z"},
                {href:"https://www.linkedin.com/company/wocs-glamping",label:"LinkedIn",d:"M4.98 3.5C4.98 4.88 3.87 6 2.5 6S.02 4.88.02 3.5C.02 2.12 1.13 1 2.5 1s2.48 1.12 2.48 2.5zM.5 8h4v13h-4zm6.5 0h3.8v1.8h.1A4.2 4.2 0 0114.6 7.7c4 0 4.7 2.6 4.7 6v7.5h-4v-6.6c0-1.6 0-3.6-2.2-3.6s-2.5 1.7-2.5 3.5v6.7H7z"},
                {href:"https://wa.me/821043370582",label:"WhatsApp",d:"M17.5 14.4l-2-1c-.3-.1-.5-.1-.7.1l-.9 1.1c-.2.2-.3.3-.6.1s-1.2-.4-2.2-1.4c-.8-.8-1.4-1.7-1.5-2s0-.5.1-.6l.4-.5.3-.4v-.5L9.2 7c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 00-.7.3A2.8 2.8 0 006.5 9c0 1.7 1.2 3.3 1.4 3.5s2.4 3.6 5.7 5.1c3.4 1.5 3.4 1 4 .9s2-1 2.2-1.9.2-1.5.2-1.7-.4-.3-.7-.5zM12 2a10 10 0 00-8.6 15L2 22l5.2-1.4A10 10 0 1012 2z"},
                {href:"https://open.kakao.com/o/kjslove1983",label:"KakaoTalk",d:"M12 3C6.5 3 2 6.6 2 11c0 2.8 1.9 5.3 4.7 6.8L5.5 21l3.8-2.2c.9.2 1.7.3 2.7.3 5.5 0 10-3.6 10-8s-4.5-8-10-8z"},
                {href:"tel:01043370582",label:"Phone",ext:false,d:"M22 16.9v3a2 2 0 01-2.2 2A19.8 19.8 0 013 5.2 2 2 0 015 3h3a2 2 0 012 1.7 12.4 12.4 0 00.7 2.6 2 2 0 01-.4 2.1L8.1 11.5a16 16 0 006.4 6.4l2.1-2.1a2 2 0 012.1-.4c.8.3 1.7.5 2.6.7A2 2 0 0122 18z"},
                {href:"mailto:info@wocs.kr",label:"Email",ext:false,d:"M4 4h16a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2zm16 2l-8 5-8-5"}
              ].map((s, i) => (
                <a key={i} href={s.href} target={s.ext !== false ? "_blank" : undefined} rel={s.ext !== false ? "noopener noreferrer" : undefined} aria-label={s.label} style={{color:`${IVORY}55`,transition:"color .3s"}} onMouseEnter={e=>e.currentTarget.style.color=GOLD} onMouseLeave={e=>e.currentTarget.style.color=`${IVORY}55`}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d={s.d}/></svg>
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>

      {/* ═══════════ FLOATING CTA ═══════════ */}
      {scrollY > 600 && (
        <div style={{
          position: "fixed", bottom: 30, right: 30, zIndex: 999,
          display: "flex", flexDirection: "column", gap: 12,
          animation: "slideUp .4s ease",
        }}>
          <button style={{
            width: 56, height: 56, borderRadius: "50%", background: GOLD, border: "none",
            color: BG, fontSize: 20, cursor: "pointer", boxShadow: `0 8px 30px ${GOLD}44`,
            display: "flex", alignItems: "center", justifyContent: "center", transition: "transform .3s",
          }}
          onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
          onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
          >
            ✆
          </button>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            style={{
              width: 56, height: 56, borderRadius: "50%", background: `${BG}dd`, border: `1px solid ${GOLD}44`,
              color: GOLD, fontSize: 16, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", transition: "transform .3s",
            }}
            onMouseEnter={e => e.currentTarget.style.transform = "scale(1.1)"}
            onMouseLeave={e => e.currentTarget.style.transform = "scale(1)"}
             >
            ↑
          </button>
        </div>
      )}
    </div>
  );
}

// Error boundary for clean console
try {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(React.createElement(WOCSHomepage));
} catch(e) {
  console.warn('WOCS render error:', e);
  document.getElementById('root').innerHTML = '<div style="color:#c9a96e;text-align:center;padding:100px;font-family:sans-serif"><h2>WOCS</h2><p>Loading...</p></div>';
}
