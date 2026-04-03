from PIL import Image
import os, zipfile

def resize_canvas(src_path, size, padding=10):
    img = Image.open(src_path).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    cw, ch = img.size
    max_w = size[0] - padding * 2
    max_h = size[1] - padding * 2
    scale = min(max_w / cw, max_h / ch)
    resized = img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    px = (size[0] - resized.width) // 2
    py = (size[1] - resized.height) // 2
    canvas.paste(resized, (px, py), resized)
    return canvas

def compress_kakao_150kb(img, out_path):
    img.save(out_path, "PNG", optimize=True, compress_level=9)
    if os.path.getsize(out_path) / 1024 <= 150:
        return
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    for colors in [128, 64, 32]:
        rgb_q = rgb.quantize(colors=colors).convert("RGB")
        result = Image.merge("RGBA", (*rgb_q.split(), a))
        result.save(out_path, "PNG", optimize=True, compress_level=9)
        if os.path.getsize(out_path) / 1024 <= 150:
            return
    print(f"  Warning {os.path.basename(out_path)}: 150KB compression failed")

for CHARACTER in ["고슴도치", "라면"]:
    src_dir = f"C:/Users/user/OneDrive/Desktop/wocs-site/이모티콘모음/{CHARACTER}"
    base_dir = src_dir

    files = sorted([f for f in os.listdir(src_dir) if f.endswith('.png') and not os.path.isdir(os.path.join(src_dir, f))])
    print(f"\n[{CHARACTER}] 원본 {len(files)}개 발견")

    platforms = {
        "kakao": {"size": (360,360), "count": 32, "icon": (78,78), "prefix": ""},
        "line":  {"size": (370,320), "count": 24, "main": (240,240), "tab": (96,74), "prefix": ""},
        "ogq":   {"size": (740,640), "count": 24, "main": (240,240), "tab": (96,74), "prefix": "O"},
    }

    for platform, cfg in platforms.items():
        out_dir = os.path.join(base_dir, platform)
        os.makedirs(out_dir, exist_ok=True)

        for i, fname in enumerate(files[:cfg["count"]], 1):
            result = resize_canvas(os.path.join(src_dir, fname), cfg["size"])
            out_path = os.path.join(out_dir, f'{cfg["prefix"]}{i:02d}.png')
            if platform == "kakao":
                compress_kakao_150kb(result, out_path)
            else:
                result.save(out_path, "PNG", optimize=True, compress_level=9)

        ref = files[0]
        if "main" in cfg:
            resize_canvas(os.path.join(src_dir, ref), cfg["main"]).save(os.path.join(out_dir, "main.png"), "PNG")
        if "tab" in cfg:
            resize_canvas(os.path.join(src_dir, ref), cfg["tab"], 4).save(os.path.join(out_dir, "tab.png"), "PNG")
        if "icon" in cfg:
            resize_canvas(os.path.join(src_dir, ref), cfg["icon"], 4).save(os.path.join(out_dir, "icon_78x78.png"), "PNG")

        zip_path = os.path.join(base_dir, f"{platform}_emoticons.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in sorted(os.listdir(out_dir)):
                zf.write(os.path.join(out_dir, f), f)
        print(f"  ✅ {platform} 완료")

    print(f"\n=== [{CHARACTER}] 카카오 용량 확인 ===")
    kakao_dir = os.path.join(base_dir, "kakao")
    fail = []
    for f in sorted(os.listdir(kakao_dir)):
        if f.endswith('.png'):
            kb = os.path.getsize(os.path.join(kakao_dir, f)) / 1024
            status = "✅" if kb <= 150 else "❌"
            if kb > 150:
                fail.append(f)
            print(f"  {status} {f}: {kb:.1f}KB")
    if not fail:
        print(f"  ✅ 전체 150KB 이하 통과!")
    else:
        print(f"  ❌ 초과 파일: {fail}")

print("\n전체 완료! 제출 순서: OGQ → 라인 → 카카오")
