# WOCS 번역 완성 가이드

## 현재 상태
- 헤더/푸터/메가메뉴: ✅ 15개 언어 완벽
- 공통 UI (91개): ✅ 15개 언어 완벽  
- 본문 상세 (1,885개): ⏳ 한국어 → API 실행 후 15개 언어

## 완성하려면 (5~10분)

### 방법 1: 새 API 키로 즉시 실행
1. https://aistudio.google.com/apikey 접속
2. "Create API key in new project" 클릭 (새 프로젝트!)
3. config.json에 새 키 입력
4. 실행:
   pip install google-genai
   python translate_all.py
5. 5~10분 대기 → 완료!

### 방법 2: 내일 실행
- 기존 API 키의 무료 할당량이 매일 초기화됨
- 내일 아침: python translate_all.py

## 나중에 한글 추가 시
1. 한글 텍스트 추가/수정
2. python translate_all.py 재실행 (새 것만 번역, 기존은 캐시 스킵)
