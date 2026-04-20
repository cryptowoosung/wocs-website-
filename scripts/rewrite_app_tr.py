"""
Surgery on src/App.jsx:
  1. Add `import TR_KO from './locales/ko.js'` and `TR_LOADERS` constant at
     module level (after existing imports / color constants).
  2. Replace the entire inline `const TR = { ... };` block with a React
     state-based lazy loader (initial bundle contains only Korean).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'src', 'App.jsx')

with open(APP, 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Locate & replace the inline TR object ─────────────────────────
m = re.search(r'(  const TR = \{)', src)
if not m:
    raise SystemExit('TR declaration not found')
tr_start = m.start()
after_open = m.end()  # right after `const TR = {`

depth = 1
i = after_open
while i < len(src) and depth > 0:
    ch = src[i]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            break
    i += 1
if depth != 0:
    raise SystemExit('Unbalanced braces')

# Advance past the closing `};` (optional trailing whitespace/newline handled by replacement)
tr_end = i + 1  # position just after the final '}'
# If `};` style, skip the semicolon too
if tr_end < len(src) and src[tr_end] == ';':
    tr_end += 1

replacement = """  // i18n lazy loader — only 'ko' is shipped in the initial bundle.
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

  const TR = trCache;"""

src = src[:tr_start] + replacement + src[tr_end:]

# ── 2. Add module-level import + TR_LOADERS after `import ReactDOM` ──
import_block = """import TR_KO from './locales/ko.js';

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
"""

# Insert after `import ReactDOM from 'react-dom/client'` line
marker = "import ReactDOM from 'react-dom/client'"
idx = src.find(marker)
if idx == -1:
    raise SystemExit('ReactDOM import line not found')
# Find the end of that line
nl = src.find('\n', idx)
insert_pos = nl + 1  # after the newline
src = src[:insert_pos] + '\n' + import_block + src[insert_pos:]

with open(APP, 'w', encoding='utf-8', newline='\n') as f:
    f.write(src)

print('App.jsx rewritten. New size:', len(src), 'chars')
