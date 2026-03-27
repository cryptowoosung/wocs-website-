import streamlit as st
import datetime
import io
import base64
import os
import urllib.request

# 라이브러리 체크
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    st.error("Pillow가 설치되지 않았습니다. 터미널에 'pip install Pillow'를 입력해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# 0. 폰트 자동 설치
# -----------------------------------------------------------------------------
def get_font_path():
    font_filename = "NanumGothic.ttf"
    if not os.path.exists(font_filename):
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        try:
            urllib.request.urlretrieve(url, font_filename)
        except:
            pass
    return font_filename

# -----------------------------------------------------------------------------
# 1. 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="WOCS 고정어닝 통합 견적", page_icon="🏛️", layout="wide")

# 사장님 정보
MY_BUSINESS_NUM = "465-02-03270"        
MY_BANK_INFO = "기업은행 323-077581-01-014 (김우성)" 

# -----------------------------------------------------------------------------
# 2. 데이터 (단가표 DB)
# -----------------------------------------------------------------------------

# 1) 다각형 (최소 2.4m)
polygon_prices = {
    "600 x 600": 96000,
    "600 x 900": 102000,
    "900 x 900": 108000,
    "1200 x 900": 114000,
    "1200 x 1200": 120000,
    "1200 x 1500": 144000,
    "1500 x 1500": 156000,
    "1800 x 1800": 192000,
    "2100 x 2100": 228000
}

# 2) 라운드형 (최소 기준 다름)
round_prices = {
    "600 x 600": 144000,
    "900 x 900": 168000,
    "1200 x 1200": 192000,
    "1500 x 1500": 216000
}

# -----------------------------------------------------------------------------
# 3. 사이드바 입력
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏛️ 고정식 어닝 견적")

    st.markdown("### 🏢 회사 로고")
    uploaded_logo = st.file_uploader("로고 이미지 업로드 (선택)", type=['png', 'jpg', 'jpeg'])
    st.markdown("---")
    
    st.markdown("### A. 형태 및 규격")
    customer_name = st.text_input("고객명 (상호)", value="고객님")
    
    # 1. 어닝 대분류 선택
    category = st.radio("어닝 종류", ["다각형 (박스/코너)", "라운드 (바가지/바나나)"], horizontal=True)
    
    # 2. 세부 형태 및 규격 설정
    if category == "다각형 (박스/코너)":
        shape_type = st.selectbox("상세 형태", ["다각형", "사각(박스형)", "코너(라운드)"])
        selected_spec = st.selectbox("규격 (높이 x 돌출)", list(polygon_prices.keys()))
        unit_price = polygon_prices[selected_spec]
        min_width = 2.4 # 다각형 기본 최소길이
        
    else: # 라운드형
        shape_type = st.selectbox("상세 형태", ["바가지형", "옆바가지형", "반 바나나형", "좌우 바나나형"])
        selected_spec = st.selectbox("규격 (높이 x 돌출)", list(round_prices.keys()))
        unit_price = round_prices[selected_spec]
        
        # 형태별 최소 기준 적용
        if shape_type in ["바가지형", "반 바나나형"]:
            min_width = 2.0
        else: # 옆바가지형, 좌우 바나나형
            min_width = 2.4

    # 3. 가로 길이 입력
    width_input = st.number_input("가로 길이 (m)", min_value=0.5, step=0.1, value=2.0)
    
    calc_width = max(width_input, min_width)
    if width_input < min_width:
        st.info(f"💡 선택하신 '{shape_type}'은 최소 {min_width}m 기준으로 계산됩니다.")

    st.markdown("### B. 원단 및 조명")
    fabric_type = st.radio("원단 종류", ["국산 (방수)", "수입 (어닝전용)"], horizontal=True)
    fabric_add_price = st.number_input("원단 추가금 (원)", value=0, step=10000)
    
    use_light = st.checkbox("T5 조명 설치")
    light_count = st.number_input("조명 개수 (개)", value=0 if not use_light else 1, step=1, disabled=not use_light)
    light_price = 20000 * light_count 

    st.markdown("### C. 기본 옵션")
    use_print = st.checkbox("로고 인쇄 (1도/1면)")
    print_price = st.number_input("인쇄비 (원)", value=0 if not use_print else 100000, step=10000, disabled=not use_print)
    
    use_gutter = st.checkbox("물받이 설치")
    default_gutter_price = int(width_input * 10000)
    gutter_price = st.number_input("물받이 가격 (원)", value=0 if not use_gutter else default_gutter_price, step=5000, disabled=not use_gutter)

    st.markdown("### D. 시공 및 부자재")
    labor_price = st.number_input("시공 노무비 (원)", value=250000, step=10000)
    material_price = st.number_input("부자재비용 (원)", value=100000, step=5000)
    transport_price = st.number_input("운송비용 (원)", value=60000, step=5000)

    st.markdown("---")
    st.markdown("### E. 현장 특수 조건")
    
    use_remove = st.checkbox("기존 철거")
    remove_price = st.number_input("철거비용 (원)", value=0 if not use_remove else 150000, step=10000, disabled=not use_remove)

    use_ladder = st.checkbox("장비 사용 (스카이)")
    ladder_price = st.number_input("장비 사용료 (원)", value=0 if not use_ladder else 500000, step=10000, disabled=not use_ladder)

    use_bracket = st.checkbox("특수 브라켓 추가")
    bracket_count = st.number_input("브라켓 개수 (개)", value=0 if not use_bracket else 1, step=1, disabled=not use_bracket)
    bracket_price = 20000 * bracket_count 

    use_special_wall = st.checkbox("특수 벽면 시공 (대리석/유리)")
    special_wall_price = st.number_input("시공비 추가 (원)", value=0 if not use_special_wall else 80000, step=10000, disabled=not use_special_wall)

    use_pole = st.checkbox("보조 기둥 설치")
    pole_price = st.number_input("기둥 설치비 (원)", value=0 if not use_pole else 100000, step=10000, disabled=not use_pole)

    use_night = st.checkbox("야간/주말 할증")
    night_price = st.number_input("할증 비용 (원)", value=0 if not use_night else 50000, step=10000, disabled=not use_night)

    st.markdown("### F. 기타/특이사항")
    note_input = st.text_input("비고 (메모)", value="")

# -----------------------------------------------------------------------------
# 4. 계산 로직
# -----------------------------------------------------------------------------
base_price = int(calc_width * unit_price)

sub_total = (base_price + fabric_add_price + light_price + print_price + gutter_price +
             labor_price + material_price + transport_price +
             remove_price + ladder_price + bracket_price + special_wall_price + pole_price + night_price)

vat = int(sub_total * 0.1)
total_price = sub_total + vat
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

spec_info_text = f"{shape_type} ({selected_spec})"
if width_input < min_width:
    spec_info_text += f" / {width_input}m (최소 {min_width}m 적용)"
else:
    spec_info_text += f" / {width_input}m"

# -----------------------------------------------------------------------------
# 5. HTML 화면 출력
# -----------------------------------------------------------------------------
logo_html = ""
if uploaded_logo is not None:
    image_bytes = uploaded_logo.getvalue()
    encoded = base64.b64encode(image_bytes).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded}" style="max-height: 80px; max-width: 200px; margin-right: 20px;">'

stamp_html = """
<div style="
    display: inline-block;
    border: 3px solid red;
    border-radius: 50%;
    width: 30px;
    height: 50px;
    text-align: center;
    line-height: 1.1;
    color: red;
    font-weight: bold;
    font-size: 13px;
    margin-left: 8px;
    vertical-align: middle;
    padding-top: 2px;
">
    김<br>우<br>성
</div>
"""

html_content = f"""
<div style="background-color: white; padding: 40px; border: 1px solid #ddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #333; font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: auto;">
<div style="border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center;">
{logo_html}
<div style="font-size: 32px; font-weight: bold;">견 적 서 <span style="font-size:18px; color:#666;">(고정식)</span></div>
</div>
<div style="text-align: right; font-size: 14px; line-height: 1.5;">
<strong>우성어닝천막공사캠프시스템 (WOCS)</strong><br>
<div style="display: flex; align-items: center; justify-content: flex-end;">
    <span>대표: 김우성</span> {stamp_html}
</div>
| 010-4337-0582<br>
사업자번호: {MY_BUSINESS_NUM}<br>
전남 화순군 사평면 유마로 592<br>
<span style="color: blue; font-weight: bold;">계좌: {MY_BANK_INFO}</span>
</div>
</div>
<div style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
<strong>수신:</strong> {customer_name} 귀하 <span style="float:right;"><strong>날짜:</strong> {today_str}</span>
</div>
<div style="font-size: 16px;">
<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;">
<span>🏷️ <strong>{spec_info_text}</strong></span>
<span style="font-weight:bold;">{base_price:,} 원</span>
</div>
"""

if fabric_add_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🧵 원단 추가 ({fabric_type})</span><span>+{fabric_add_price:,} 원</span></div>"""
if use_print and print_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🎨 로고 인쇄</span><span>+{print_price:,} 원</span></div>"""
if use_light and light_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>💡 T5 조명 ({light_count}개)</span><span>+{light_price:,} 원</span></div>"""
if use_gutter and gutter_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>💧 물받이 설치</span><span>+{gutter_price:,} 원</span></div>"""

if use_remove and remove_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🏗️ 기존 철거</span><span>+{remove_price:,} 원</span></div>"""
if use_ladder and ladder_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🚛 장비 사용 (스카이)</span><span>+{ladder_price:,} 원</span></div>"""
if use_bracket and bracket_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🔧 특수 브라켓 ({bracket_count}개)</span><span>+{bracket_price:,} 원</span></div>"""
if use_special_wall and special_wall_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🧱 특수 벽면 시공</span><span>+{special_wall_price:,} 원</span></div>"""
if use_pole and pole_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🏛️ 보조 기둥 설치</span><span>+{pole_price:,} 원</span></div>"""
if use_night and night_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🌙 야간/주말 할증</span><span>+{night_price:,} 원</span></div>"""

html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>👷 시공 노무비</span><span>+{labor_price:,} 원</span></div>"""
if material_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🔩 부자재비용</span><span>+{material_price:,} 원</span></div>"""
if transport_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🚚 운송비용</span><span>+{transport_price:,} 원</span></div>"""

html_content += f"""
</div>
<div style="margin-top: 40px; text-align: right;">
<div style="font-size: 16px; color: #555; margin-bottom: 5px;">공급가액: {sub_total:,} 원</div>
<div style="font-size: 16px; color: #555; margin-bottom: 10px;">부가세(VAT): {vat:,} 원</div>
<div style="font-size: 28px; font-weight: bold; color: #d9534f; border-top: 2px solid #333; padding-top: 15px; display: inline-block;">총 견적 금액: {total_price:,} 원</div>
</div>
<div style="margin-top: 30px; font-size: 14px; color: #555; border-top: 1px dashed #ccc; padding-top: 20px;">
{'<strong>※ 특이사항:</strong> ' + note_input + '<br>' if note_input else ''}
<strong>1. 견적 유효기간:</strong> 견적일로부터 10일<br>
<strong>2. 하자 보증기간:</strong> 납품일로부터 1년 (천재지변 및 사용자 과실 제외)<br>
<strong style="color:red;">3. 결제방법:</strong> 선금 50% / 잔금 50% (시공 완료 즉시)
</div>
<br><br>
<div style="text-align:center; color:#888; font-size:13px;">귀하의 무궁한 발전을 기원합니다.</div>
</div>
"""

st.markdown(html_content, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 이미지 저장
# -----------------------------------------------------------------------------
def create_image():
    width, height = 800, 1450
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    font_path = get_font_path()
    try:
        font_L = ImageFont.truetype(font_path, 40)
        font_M = ImageFont.truetype(font_path, 25)
        font_S = ImageFont.truetype(font_path, 20)
        font_Bold = ImageFont.truetype(font_path, 25)
        font_Stamp = ImageFont.truetype(font_path, 14)
    except:
        font_L = ImageFont.load_default()
        font_M = ImageFont.load_default()
        font_S = ImageFont.load_default()
        font_Bold = ImageFont.load_default()
        font_Stamp = ImageFont.load_default()

    if uploaded_logo is not None:
        try:
            logo_img = Image.open(uploaded_logo)
            aspect_ratio = logo_img.width / logo_img.height
            new_height = 80
            new_width = int(new_height * aspect_ratio)
            logo_img = logo_img.resize((new_width, new_height))
            img.paste(logo_img, (50, 40))
        except:
            pass

    draw.text((320, 50), "견  적  서", font=font_L, fill="black")
    draw.text((500, 65), "(고정식)", font=font_S, fill="#666")

    draw.line((50, 130, 750, 130), fill="black", width=2)
    
    draw.text((450, 150), "우성어닝천막공사캠프시스템 (WOCS)", font=font_Bold, fill="black")
    draw.text((450, 190), "대표: 김우성", font=font_S, fill="black")

    # 도장
    stamp_x = 580
    stamp_y = 178
    stamp_w = 30
    stamp_h = 50
    draw.ellipse((stamp_x, stamp_y, stamp_x + stamp_w, stamp_y + stamp_h), outline="red", width=2)
    draw.text((stamp_x + 8, stamp_y + 4), "김", font=font_Stamp, fill="red")
    draw.text((stamp_x + 8, stamp_y + 18), "우", font=font_Stamp, fill="red")
    draw.text((stamp_x + 8, stamp_y + 32), "성", font=font_Stamp, fill="red")

    # 정보
    text_start_y = 245
    draw.text((450, text_start_y), f"사업자번호: {MY_BUSINESS_NUM}", font=font_S, fill="black")
    draw.text((450, text_start_y + 25), "전남 화순군 사평면 유마로 592", font=font_S, fill="black")
    draw.text((450, text_start_y + 50), "Tel: 010-4337-0582", font=font_S, fill="black")
    draw.text((450, text_start_y + 75), f"{MY_BANK_INFO}", font=font_S, fill="blue")

    draw.text((50, 170), f"수신: {customer_name} 귀하", font=font_M, fill="black")
    draw.text((50, 210), f"날짜: {today_str}", font=font_M, fill="black")

    line_y = 380 
    draw.line((50, line_y, 750, line_y), fill="gray", width=1)
    y = line_y + 30
    def draw_row(name, price):
        nonlocal y
        draw.text((50, y), name, font=font_M, fill="black")
        draw.text((750, y), f"{price:,} 원", font=font_M, fill="black", anchor="ra")
        y += 50

    draw_row(f"{spec_info_text}", base_price)
    
    if fabric_add_price > 0: draw_row(f"원단 추가 ({fabric_type})", fabric_add_price)
    if use_print and print_price > 0: draw_row("로고 인쇄", print_price)
    if use_light and light_price > 0: draw_row(f"T5 조명 ({light_count}개)", light_price)
    if use_gutter and gutter_price > 0: draw_row("물받이 설치", gutter_price)
    
    if use_remove and remove_price > 0: draw_row("기존 철거", remove_price)
    if use_ladder and ladder_price > 0: draw_row("장비 사용 (스카이)", ladder_price)
    if use_bracket and bracket_price > 0: draw_row(f"특수 브라켓 ({bracket_count}개)", bracket_price)
    if use_special_wall and special_wall_price > 0: draw_row("특수 벽면 시공", special_wall_price)
    if use_pole and pole_price > 0: draw_row("보조 기둥 설치", pole_price)
    if use_night and night_price > 0: draw_row("야간/주말 할증", night_price)
    
    draw_row("시공 노무비", labor_price)
    if material_price > 0: draw_row("부자재비용", material_price)
    if transport_price > 0: draw_row("운송비용", transport_price)

    draw.line((50, y+10, 750, y+10), fill="black", width=2)
    y += 40
    draw.text((400, y), "공급가액:", font=font_S, fill="gray")
    draw.text((750, y), f"{sub_total:,} 원", font=font_S, fill="gray", anchor="ra")
    y += 30
    draw.text((400, y), "부가세(VAT):", font=font_S, fill="gray")
    draw.text((750, y), f"{vat:,} 원", font=font_S, fill="gray", anchor="ra")
    y += 50
    draw.text((400, y), "총 견적 금액:", font=font_Bold, fill="red")
    draw.text((750, y), f"{total_price:,} 원", font=font_Bold, fill="red", anchor="ra")
    
    y += 70
    if note_input:
        draw.text((50, y), f"※ 특이사항: {note_input}", font=font_S, fill="black")
        y += 40
    draw.text((50, y), "1. 견적 유효기간: 견적일로부터 10일", font=font_S, fill="gray")
    y += 30
    draw.text((50, y), "2. 하자 보증기간: 납품일로부터 1년 (천재지변 및 사용자 과실 제외)", font=font_S, fill="gray")
    
    # ★★★ 결제조건 추가됨 ★★★
    y += 30
    draw.text((50, y), "3. 결제방법: 선금 50% / 잔금 50% (시공 완료 즉시)", font=font_S, fill="black")
    
    y += 50
    draw.line((50, y, 750, y), fill="gray", width=1)
    y += 20
    draw.text((50, y), "위 견적 내용을 확인하였으며, 이에 승인하고 계약을 체결합니다.", font=font_S, fill="black")
    y += 40
    draw.text((400, y), "주문 승인 (서명): __________________", font=font_M, fill="black")

    y += 60
    draw.text((250, y), "귀하의 무궁한 발전을 기원합니다.", font=font_S, fill="gray")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

st.write("")
st.write("")
col_dn1, col_dn2 = st.columns([4, 1])
with col_dn2:
    st.download_button("💾 견적서 이미지 저장", create_image(), f"고정식견적_{customer_name}_{today_str}.png", "image/png", use_container_width=True)