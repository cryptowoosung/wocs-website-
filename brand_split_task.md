wocs.kr을 글램핑 전용 사이트로 정리한다. 어닝·천막은 자매 사이트 glampingtentgo.com(우성어닝)이 담당하므로, 
wocs.kr에서는 어닝·천막을 주력 키워드에서 빼고 안내 링크만 남긴다.
순서대로 진행하고 각 단계 검증 후 다음으로 넘어가라. 실패하면 원인을 찾아 재검증하라. 확인 질문 없이 진행하라.

[0단계: 준비]
0-1. git checkout main && git pull && git checkout -b feat/brand-split-glamping-only
0-2. 현재 상태 파악: grep -rn "어닝\|천막" --include="*.html" --include="*.json" --include="*.py" --include="*.js" . 
     | grep -v "content/auto_post" | grep -v node_modules | grep -v ".bkit" 결과를 파일별 건수 표로 출력하라.
     (content/auto_post는 블로그 본문이라 제외. 상호명 "우성어닝천막공사캠프시스템"은 법적 상호이므로 건드리지 않는다.)

[1단계: 홈페이지 index.html 타이틀·메타 재작성]
1-1. <title>을 정확히 다음으로: 
     글램핑텐트 제작 시공 전문 WOCS | 특허 무용접 돔·사파리텐트 | 화순 전남
1-2. <meta name="description">을 정확히 다음으로:
     16년 경력 글램핑 시공 전문. 특허 무용접 조인트로 3일 완성. 지오데식 돔·사파리텐트·모듈러 글램핑 직접 제작, 전국 시공. 전남 화순 쇼룸 운영.
1-3. og:title, og:description, twitter:title, twitter:description도 위와 동일하게 맞춰라.
1-4. <h1>은 그대로 둔다 (이미 글램핑 중심).
1-5. index.html 내 "어닝·천막" 또는 "어닝, 천막" 같이 제품 카테고리로 나열된 문구가 있으면 찾아 출력하고, 
     제품 나열 맥락이면 제거하고 상호명 맥락이면 유지하라. 판단이 애매한 건 출력만 하고 건드리지 마라.
1-6. 검증: grep -n "<title>\|name=\"description\"\|og:title\|og:description" index.html 출력. 
     title ≤60자, description ≤160자 확인.

[2단계: JSON-LD 구조화 데이터 정리]
2-1. index.html 및 공용 include 파일에서 JSON-LD(LocalBusiness/Organization)를 찾아라.
2-2. name 필드가 "우성어닝천막공사캠프시스템"이면 유지 (법적 상호, NAP 통일 규칙). 
     description, knowsAbout, makesOffer, hasOfferCatalog 등에서 어닝·천막 항목이 있으면 글램핑 항목으로 교체하라.
2-3. sameAs 배열에 https://glampingtentgo.com 이 없으면 추가하라 (자매 사이트).
2-4. 검증: python -c "import json,re,sys; h=open('index.html',encoding='utf-8').read(); 
     [json.loads(m) for m in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', h, re.S)]; print('JSON-LD OK')"

[3단계: 어닝·천막 안내 링크 추가]
3-1. 공용 푸터(#wocs-footer 또는 footer include)를 찾아라. 여러 파일에 하드코딩돼 있으면 그 파일 목록을 출력하라.
3-2. 사업자 정보 줄(biz-line) 바로 위에 다음 한 줄을 추가하라 (모든 페이지에 적용되도록):
     <p class="sister-site" style="font-size:12px;margin:8px 0 0"><a href="https://glampingtentgo.com/" rel="noopener" target="_blank">어닝·천막·전동어닝 시공은 자매 브랜드 우성어닝 →</a></p>
     기존 푸터 스타일(색상 변수 등)에 맞춰 style은 조정해도 된다. 문구는 유지하라.
3-3. resources/faq.html에 FAQ 항목 하나 추가 (기존 faq-item 마크업 형식 그대로):
     Q: 어닝이나 천막 시공도 하나요?
     A: 네. 어닝·천막·전동어닝·창고 천막은 자매 브랜드 우성어닝(glampingtentgo.com)에서 전문으로 시공합니다. 같은 대표가 운영하며 화순 본사에서 직접 제작합니다.
     FAQPage JSON-LD가 있으면 거기에도 같은 Q/A를 추가하라.
3-4. 검증: grep -rl "glampingtentgo.com" --include="*.html" . | grep -v content/ | wc -l → 푸터가 들어간 페이지 수와 같아야 한다(최소 50 이상).

[4단계: 자동 블로그 생성기 주제 범위 조정]
4-1. auto_writer.py의 주제 풀/카테고리/프롬프트에서 어닝·천막 관련 주제가 있으면 목록으로 출력하라.
4-2. 있으면 제거하고, 시스템 프롬프트에 다음 규칙을 추가하라:
     "이 사이트는 글램핑 전용이다. 어닝·천막·전동어닝을 주제로 글을 쓰지 마라. 본문에서 어닝·천막을 언급해야 하면 
      '자매 브랜드 우성어닝(https://glampingtentgo.com)'으로 한 번만 안내하라."
4-3. 검증: pytest tests/ -q → 전부 통과. --dry-run 1회 실행해 어닝 주제가 안 뽑히는지 확인 (발행 금지).

[5단계: sitemap·llms.txt 갱신]
5-1. llms.txt가 있으면 사이트 설명에서 어닝·천막을 빼고 글램핑 전용임을 명시, 자매 사이트 glampingtentgo.com 한 줄 추가.
5-2. sitemap 재생성 (update_sitemap.py). 수정된 파일만 lastmod가 오늘로 바뀌는지 확인.

[6단계: 커밋·머지·배포 검증]
6-1. git add -A && git commit -m "feat(brand): wocs.kr glamping-only — move awning/tent keywords to sister site glampingtentgo.com"
6-2. git checkout main && git merge feat/brand-split-glamping-only && git push origin main
6-3. 120초 대기 후:
     curl -s https://wocs.kr/ | grep -o "<title>[^<]*" → "글램핑텐트 제작 시공 전문 WOCS" 포함
     curl -s https://wocs.kr/ | grep -o 'name="description" content="[^"]*"' → "어닝" 미포함
     curl -s https://wocs.kr/ | grep -c "glampingtentgo.com" → 1 이상
     curl -s https://wocs.kr/resources/faq.html | grep -c "우성어닝" → 1 이상
     curl -s https://wocs.kr/products/dome-tent.html | grep -c "glampingtentgo.com" → 1 이상 (푸터 전파 확인)
6-4. 결과를 | 검증 | 기대값 | 실제값 | 판정 | 표로 출력하라. 0-2에서 출력한 "어닝·천막" 건수 표의 before/after도 함께 출력하라.