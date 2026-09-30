import os
import re
import json
import math
import shutil
import qrcode
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

UPLOAD_DIR = r"C:\Users\Hp\.gemini\antigravity\brain\c965a89a-0904-4773-a34c-b5ffdc4369f0\.user_uploaded"
EXTERIOR_UPLOAD = os.path.join(UPLOAD_DIR, "media_1790480003615.jpg")
WORDMARK_UPLOAD = os.path.join(UPLOAD_DIR, "media_1790480117250.png")
EMBLEM_UPLOAD = os.path.join(UPLOAD_DIR, "media_1790480125343.jpg")


def load_config(config_path="config.js"):
    """Parse config.js and extract JSON settings."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"window\.RESTAURANT_CONFIG\s*=\s*(\{.*?\});", content, re.DOTALL)
    if not match:
        return {}
    json_str = match.group(1)
    json_str = re.sub(r"//.*", "", json_str)
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    try:
        return json.loads(json_str)
    except Exception:
        return {}


def get_font(size, bold=False, italic=False, serif=False):
    """Load Windows system fonts cleanly with fallbacks."""
    candidates = []
    if serif and italic:
        candidates = ["georgiai.ttf", "timesbi.ttf", "timesi.ttf", "ariali.ttf"]
    elif serif and bold:
        candidates = ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"]
    elif serif:
        candidates = ["georgia.ttf", "times.ttf", "arial.ttf"]
    elif bold and italic:
        candidates = ["arialbi.ttf", "georgiabi.ttf", "timesbi.ttf"]
    elif bold:
        candidates = ["arialbd.ttf", "segoeuib.ttf", "georgiab.ttf", "timesbd.ttf"]
    elif italic:
        candidates = ["ariali.ttf", "georgiai.ttf", "timesi.ttf"]
    else:
        candidates = ["arial.ttf", "segoeui.ttf", "georgia.ttf"]

    for font_name in candidates:
        font_path = os.path.join("C:\\Windows\\Fonts", font_name)
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def prepare_brand_assets():
    """
    Process the 3 user-uploaded Mudoven files into ultra-luxury transparent & cropped assets:
    1. source_exterior.jpg -> ambience_1.jpg, ambience_2.jpg, ambience_3.jpg
    2. source_emblem.jpg   -> logo_with_gold_rim.png & logo.png (Circular M Cafe emblem with 24k Gold Rim)
    3. source_wordmark.png -> mudoven_title.png (Transparent cursive 'Mudoven' in Flame Orange +
                              'YOUR FOREVER HAPPY PLACE ®' & 'EST. 2012' in 24k Champagne Gold)
    """
    if os.path.exists(EXTERIOR_UPLOAD) and not os.path.exists("source_exterior.jpg"):
        shutil.copyfile(EXTERIOR_UPLOAD, "source_exterior.jpg")
    if os.path.exists(WORDMARK_UPLOAD) and not os.path.exists("source_wordmark.png"):
        shutil.copyfile(WORDMARK_UPLOAD, "source_wordmark.png")
    if os.path.exists(EMBLEM_UPLOAD) and not os.path.exists("source_emblem.jpg"):
        shutil.copyfile(EMBLEM_UPLOAD, "source_emblem.jpg")

    # 1. Create Ambience Thumbnails from Mudoven Night Exterior Photo
    if os.path.exists("source_exterior.jpg"):
        ext = Image.open("source_exterior.jpg").convert("RGB")
        ew, eh = ext.size

        # ambience_1.jpg: Full iconic glass facade & night sky view (centered architectural crop)
        c1 = ext.crop((0, int(eh * 0.14), ew, int(eh * 0.84)))
        c1 = ImageEnhance.Color(ImageEnhance.Contrast(c1).enhance(1.12)).enhance(1.15)
        c1.save("ambience_1.jpg", quality=94)

        # ambience_2.jpg: Focused & centered directly on the top 'MUDOVEN' glowing neon sign + golden atrium below it
        c2 = ext.crop((int(ew * 0.45), int(eh * 0.21), int(ew * 0.96), int(eh * 0.56)))
        c2 = ImageEnhance.Color(ImageEnhance.Contrast(c2).enhance(1.16)).enhance(1.20)
        c2.save("ambience_2.jpg", quality=95)

        # ambience_3.jpg: Grand Entrance ('Mudoven' neon script, 'मड ओवन' wall & warm cove palms)
        c3 = ext.crop((int(ew * 0.04), int(eh * 0.44), int(ew * 0.96), int(eh * 0.78)))
        c3 = ImageEnhance.Color(ImageEnhance.Contrast(c3).enhance(1.12)).enhance(1.15)
        c3.save("ambience_3.jpg", quality=94)
        print("[OK] Generated ambience_1.jpg, ambience_2.jpg, ambience_3.jpg from uploaded Mudoven photo")

    # 2. Create 24k Gold-Rimmed Circular Logo Medallion from source_emblem.jpg
    if os.path.exists("source_emblem.jpg"):
        emb = Image.open("source_emblem.jpg").convert("RGB")
        arr = np.array(emb)
        # Find bounding box of non-white content (exclude right-edge scrollbar line if present)
        h_e, w_e, _ = arr.shape
        arr[:, int(w_e * 0.96):, :] = 255
        mask_nonwhite = (arr[:, :, 0] < 240) | (arr[:, :, 1] < 240) | (arr[:, :, 2] < 240)
        ys, xs = np.where(mask_nonwhite)
        if len(xs) > 0 and len(ys) > 0:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()
            cx = (x_min + x_max) // 2
            cy = (y_min + y_max) // 2
            radius = int(max(x_max - x_min, y_max - y_min) * 0.54)
            crop_box = (
                max(0, cx - radius),
                max(0, cy - radius),
                min(w_e, cx + radius),
                min(h_e, cy + radius),
            )
            emb_crop = Image.fromarray(arr).crop(crop_box)
        else:
            emb_crop = emb

        size = 600
        emb_crop = emb_crop.resize((size - 56, size - 56), Image.Resampling.LANCZOS)

        medallion = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        mdraw = ImageDraw.Draw(medallion)

        # Outer 24k Gold Ring
        mdraw.ellipse([4, 4, size - 5, size - 5], fill=(212, 175, 55, 255), outline=(248, 226, 152, 255), width=6)
        mdraw.ellipse([16, 16, size - 17, size - 17], fill=(150, 115, 28, 255))
        mdraw.ellipse([22, 22, size - 23, size - 23], fill=(255, 255, 255, 255))

        # Circular mask for emblem
        circle_mask = Image.new("L", (size - 56, size - 56), 0)
        cdraw = ImageDraw.Draw(circle_mask)
        cdraw.ellipse([0, 0, size - 57, size - 57], fill=255)

        medallion.paste(emb_crop.convert("RGBA"), (28, 28), mask=circle_mask)

        # Inner hairline gold ring
        mdraw.ellipse([25, 25, size - 26, size - 26], outline=(212, 175, 55, 220), width=4)

        medallion.save("logo_with_gold_rim.png")
        medallion.save("logo.png")
        print("[OK] Generated logo_with_gold_rim.png & logo.png (24k Gold Rim Medallion)")

    # 3. Create Transparent Luxury Wordmark (mudoven_title.png) from source_wordmark.png
    if os.path.exists("source_wordmark.png"):
        wm = Image.open("source_wordmark.png").convert("RGB")
        w_arr = np.array(wm, dtype=np.float32)

        # Ignore top-left 18% corner smudge and use strict stroke threshold (lum < 205) for tight bounding box
        lum = 0.299 * w_arr[:, :, 0] + 0.587 * w_arr[:, :, 1] + 0.114 * w_arr[:, :, 2]
        h_w, w_w = lum.shape
        stroke_mask = lum < 205
        stroke_mask[:int(h_w * 0.22), :int(w_w * 0.35)] = False
        ys, xs = np.where(stroke_mask)
        if len(xs) > 0 and len(ys) > 0:
            pad_x, pad_y = 24, 18
            x1 = max(0, int(xs.min()) - pad_x)
            y1 = max(0, int(ys.min()) - pad_y)
            x2 = min(w_arr.shape[1], int(xs.max()) + pad_x)
            y2 = min(w_arr.shape[0], int(ys.max()) + pad_y)
            w_arr = w_arr[y1:y2, x1:x2]
            lum = lum[y1:y2, x1:x2]

        r, g, b = w_arr[:, :, 0], w_arr[:, :, 1], w_arr[:, :, 2]
        # Alpha based on distance from white background
        max_channel_drop = np.maximum(np.maximum(255.0 - r, 255.0 - g), 255.0 - b)
        alpha = np.clip((max_channel_drop - 18.0) / 55.0, 0.0, 1.0) ** 0.85

        # Distinguish orange script ('Mudoven') vs dark text ('YOUR FOREVER HAPPY PLACE ®' & 'EST. 2012')
        orange_ness = (r - b)
        is_orange = orange_ness > 65

        out_rgba = np.zeros((w_arr.shape[0], w_arr.shape[1], 4), dtype=np.uint8)

        # Vibrant Mudoven Flame-Orange for 'Mudoven' script
        out_rgba[:, :, 0] = np.where(is_orange, np.clip(r * 1.06 + 10, 235, 255), 247).astype(np.uint8)
        out_rgba[:, :, 1] = np.where(is_orange, np.clip(g * 1.05 + 6, 92, 135), 223).astype(np.uint8)
        out_rgba[:, :, 2] = np.where(is_orange, np.clip(b * 0.85, 24, 55), 148).astype(np.uint8)
        out_rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

        fg_img = Image.fromarray(out_rgba, "RGBA")

        # Add soft dark + warm gold drop shadow for maximum legibility over architectural photo
        s_arr = np.zeros_like(out_rgba)
        s_arr[:, :, 3] = (alpha * 210).astype(np.uint8)
        shadow_img = Image.fromarray(s_arr, "RGBA").filter(ImageFilter.GaussianBlur(radius=6))

        canvas_wm = Image.new("RGBA", (fg_img.width + 20, fg_img.height + 20), (0, 0, 0, 0))
        canvas_wm.paste(shadow_img, (10, 14), mask=shadow_img)
        canvas_wm.paste(fg_img, (10, 10), mask=fg_img)
        canvas_wm.save("mudoven_title.png")
        print("[OK] Generated mudoven_title.png (Transparent Flame-Orange & 24k Gold Wordmark)")


def create_ambience_luxury_background(width=1200, height=1800):
    """
    Create an Ultra-Luxury Mudoven Ambience Background directly from the user's attached
    Mudoven night exterior photo (source_exterior.jpg).
    """
    y_idx = np.linspace(0, 1, height)[:, None]
    x_idx = np.linspace(0, 1, width)[None, :]

    r_base = (8 * (1 - y_idx) + 6 * y_idx)
    g_base = (12 * (1 - y_idx) + 9 * y_idx)
    b_base = (24 * (1 - y_idx) + 16 * y_idx)

    dist_top = np.sqrt(((x_idx - 0.5) / 0.52) ** 2 + ((y_idx - 0.16) / 0.22) ** 2)
    glow_top = np.clip(1.0 - dist_top, 0, 1) ** 1.8

    dist_mid = np.sqrt(((x_idx - 0.5) / 0.58) ** 2 + ((y_idx - 0.45) / 0.30) ** 2)
    glow_mid = np.clip(1.0 - dist_mid, 0, 1) ** 2.0

    r_grad = r_base + glow_top * 52 + glow_mid * 38
    g_grad = g_base + glow_top * 34 + glow_mid * 26
    b_grad = b_base + glow_top * 14 + glow_mid * 8

    grad_arr = np.stack([
        np.clip(r_grad, 0, 255),
        np.clip(g_grad, 0, 255),
        np.clip(b_grad, 0, 255)
    ], axis=2).astype(np.uint8)
    base_img = Image.fromarray(grad_arr, "RGB")

    amb_path = "source_exterior.jpg" if os.path.exists("source_exterior.jpg") else (
        EXTERIOR_UPLOAD if os.path.exists(EXTERIOR_UPLOAD) else None
    )
    if amb_path:
        try:
            amb = Image.open(amb_path).convert("RGB")
            aw, ah = amb.size
            target_ratio = width / height
            src_ratio = aw / ah
            if src_ratio > target_ratio:
                new_w = int(ah * target_ratio)
                left = (aw - new_w) // 2
                amb = amb.crop((left, 0, left + new_w, ah))
            else:
                new_h = int(aw / target_ratio)
                top = (ah - new_h) // 2
                amb = amb.crop((0, top, aw, top + new_h))
            amb = amb.resize((width, height), Image.Resampling.LANCZOS)

            amb_sharp = ImageEnhance.Contrast(amb).enhance(1.18)
            amb_sharp = ImageEnhance.Color(amb_sharp).enhance(1.22)
            amb_soft = amb_sharp.filter(ImageFilter.GaussianBlur(radius=2.6))

            amb_arr = np.array(amb_soft, dtype=np.float32)
            base_arr = np.array(base_img, dtype=np.float32)

            edge_dist = np.sqrt(((x_idx - 0.5) / 0.68) ** 2 + ((y_idx - 0.44) / 0.52) ** 2)
            photo_weight = np.clip(0.58 - 0.30 * (edge_dist ** 1.5), 0.22, 0.58)[:, :, None]

            blended = base_arr * (1.0 - photo_weight) + amb_arr * photo_weight
            base_img = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "RGB")
        except Exception as e:
            print("Ambience blend warning:", e)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    cx, cy = width // 2, 185
    for r_arch, alpha_val in [(230, 26), (305, 20), (390, 14), (480, 10)]:
        odraw.ellipse(
            [cx - r_arch, cy - int(r_arch * 0.75), cx + r_arch, cy + int(r_arch * 0.75)],
            outline=(247, 223, 148, alpha_val),
            width=2
        )

    for angle_deg in range(0, 360, 15):
        rad = math.radians(angle_deg)
        x1 = cx + int(110 * math.cos(rad))
        y1 = 135 + int(110 * math.sin(rad))
        x2 = cx + int(195 * math.cos(rad))
        y2 = 135 + int(195 * math.sin(rad))
        odraw.line([x1, y1, x2, y2], fill=(212, 175, 55, 18), width=1)

    base_rgba = base_img.convert("RGBA")
    base_rgba = Image.alpha_composite(base_rgba, overlay)
    return base_rgba.convert("RGB")


def draw_indri_luxury_borders(draw, width=1200, height=1800):
    """
    Draw the signature luxury 24k Gold double border with ornamental corner accents.
    """
    gold_outer = (212, 175, 55)
    gold_inner = (165, 132, 42)
    gold_bright = (247, 223, 148)

    m1 = 36
    draw.rectangle([m1, m1, width - m1, height - m1], outline=gold_outer, width=4)

    m2 = 52
    draw.rectangle([m2, m2, width - m2, height - m2], outline=gold_inner, width=1)

    c_len = 42
    for cx, cy, dx, dy in [
        (m2 + 10, m2 + 10, 1, 1),
        (width - m2 - 10, m2 + 10, -1, 1),
        (m2 + 10, height - m2 - 10, 1, -1),
        (width - m2 - 10, height - m2 - 10, -1, -1),
    ]:
        draw.line([cx, cy, cx + dx * c_len, cy], fill=gold_bright, width=2)
        draw.line([cx, cy, cx, cy + dy * c_len], fill=gold_bright, width=2)
        draw.polygon([(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)], fill=gold_bright)


def draw_sparkle(draw, cx, cy, radius=12, color=(212, 175, 55)):
    """Draw a 4-point luxury star sparkle."""
    r_outer = radius
    r_inner = max(2, int(radius * 0.28))
    pts = []
    for i in range(8):
        angle = i * (math.pi / 4.0) - (math.pi / 2.0)
        r = r_outer if i % 2 == 0 else r_inner
        px = cx + math.cos(angle) * r
        py = cy + math.sin(angle) * r
        pts.append((px, py))
    draw.polygon(pts, fill=color)


def draw_star_5pt(draw, cx, cy, radius=9, color=(212, 175, 55)):
    """Draw a crisp 5-pointed gold rating star."""
    r_outer = radius
    r_inner = radius * 0.42
    pts = []
    for i in range(10):
        angle = i * (math.pi / 5.0) - (math.pi / 2.0)
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(pts, fill=color)


def draw_5_stars_row(draw, start_x, cy, star_radius=8, spacing=20, color=(212, 165, 32)):
    """Draw a row of 5 gold stars."""
    for i in range(5):
        draw_star_5pt(draw, start_x + i * spacing, cy, radius=star_radius, color=color)


def draw_google_g_icon(draw, cx, cy, radius=14):
    """Draw a clean Google 'G' multi-color icon inside a white circle."""
    draw.ellipse([cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3], fill=(255, 255, 255))
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.pieslice(bbox, 220, 325, fill=(234, 67, 53))
    draw.pieslice(bbox, 135, 220, fill=(251, 188, 5))
    draw.pieslice(bbox, 45, 135, fill=(52, 168, 83))
    draw.pieslice(bbox, 345, 45, fill=(66, 133, 244))
    inner_r = int(radius * 0.56)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(255, 255, 255))
    draw.rectangle([cx, cy - int(radius * 0.22), cx + radius, cy + int(radius * 0.24)], fill=(66, 133, 244))


def draw_instagram_icon(draw, cx, cy, size=26):
    """Draw a clean Instagram camera glyph."""
    half = size // 2
    draw.rounded_rectangle(
        [cx - half, cy - half, cx + half, cy + half],
        radius=7,
        fill=(214, 41, 118),
        outline=(255, 255, 255),
        width=2
    )
    r_lens = int(size * 0.24)
    draw.ellipse([cx - r_lens, cy - r_lens, cx + r_lens, cy + r_lens], outline=(255, 255, 255), width=2)
    draw.ellipse([cx + half - 7, cy - half + 4, cx + half - 4, cy - half + 7], fill=(255, 255, 255))


def generate_styled_qr(url, box_size=16, border=2, fill_color=(12, 16, 28), back_color=(255, 255, 255)):
    """Generate a high-contrast, ultra-scannable QR code image."""
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    return img


def draw_brand_header(canvas, draw, w=1200):
    """
    Draw the Compact & Balanced Mudoven Cafe Luxury Header (Leaves Generous Center Breathing Room):
    1. 24k Gold Rim Circular M Cafe / MudOven Cafe Medallion (158px)
    2. Official 'Mudoven' Script Wordmark ('Your Forever Happy Place • Est. 2012')
    3. 'M U D O V E N   C A F E   •   E S T .   2 0 1 2' in 24k Brushed Gold
    4. 'YOUR FOREVER HAPPY PLACE  •  WE SPEAK THE GOOD FOOD LANGUAGE' in crisp white
    5. Ornamental 24k Gold Divider with Central Diamond at y=448 (freeing ~100px for center section!)
    """
    logo_path = "logo_with_gold_rim.png" if os.path.exists("logo_with_gold_rim.png") else "logo.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 158
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        canvas.paste(logo, (int((w - logo_size) / 2), 46), mask=logo)

    title_path = "mudoven_title.png"
    if os.path.exists(title_path):
        title_img = Image.open(title_path).convert("RGBA")
        target_w = 370
        target_h = int(title_img.size[1] * (target_w / title_img.size[0]))
        if target_h > 142:
            target_h = 142
            target_w = int(title_img.size[0] * (target_h / title_img.size[1]))
        title_img = title_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        hx = int((w - target_w) / 2) + 10
        hy = 202
        canvas.paste(title_img, (hx, hy), mask=title_img)

    font_midway = get_font(28, bold=True)
    midway_text = "M U D O V E N   C A F E   •   E S T .   2 0 1 2"
    bbox = draw.textbbox((0, 0), midway_text, font=font_midway)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 354), midway_text, fill=(247, 223, 148), font=font_midway)

    font_sub = get_font(18, bold=True)
    sub_text = "YOUR FOREVER HAPPY PLACE  •  WE SPEAK THE GOOD FOOD LANGUAGE"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 396), sub_text, fill=(255, 255, 255), font=font_sub)

    div_y = 438
    draw.line([200, div_y, w - 200, div_y], fill=(212, 175, 55), width=2)
    draw.polygon([(w // 2, div_y - 7), (w // 2 + 7, div_y), (w // 2, div_y + 7), (w // 2 - 7, div_y)], fill=(247, 223, 148))


def draw_footer(canvas, draw, w=1200):
    """
    Draw the Ultra-Luxury Dual-Outlet Address & Phone Box (Vijay Nagar First, then Rau)
    + Gold Sparkle Thank-You Footer for effortless readability on printed standees & cards.
    """
    font_label = get_font(22, bold=True)
    font_addr = get_font(22, bold=True)
    font_phone = get_font(34, bold=True)
    font_thanks = get_font(28, bold=False, italic=True, serif=True)

    info_x1, info_y1 = 82, 1450
    info_x2, info_y2 = w - 82, 1662

    glass = Image.new("RGBA", (w, 1800), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glass)
    # Outer 24k Gold Box
    gdraw.rounded_rectangle(
        [info_x1, info_y1, info_x2, info_y2],
        radius=18,
        fill=(8, 12, 22, 242),
        outline=(212, 175, 55, 255),
        width=3
    )
    # Inner hairline gold border
    gdraw.rounded_rectangle(
        [info_x1 + 6, info_y1 + 6, info_x2 - 6, info_y2 - 6],
        radius=14,
        outline=(247, 223, 148, 90),
        width=1
    )
    # Subtle gold divider line between Vijay Nagar and Rau addresses
    div_y = info_y1 + 62
    gdraw.line([info_x1 + 90, div_y, info_x2 - 90, div_y], fill=(212, 175, 55, 115), width=1)

    # Prominent 24k Gold Call Pill behind Phone Number
    gdraw.rounded_rectangle(
        [info_x1 + 135, info_y1 + 124, info_x2 - 135, info_y2 - 16],
        radius=14,
        fill=(212, 175, 55, 38),
        outline=(249, 226, 156, 165),
        width=2
    )
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba = Image.alpha_composite(canvas_rgba, glass)
    canvas.paste(canvas_rgba.convert("RGB"))

    # 1. FIRST ADDRESS: Vijay Nagar (The Hub, Scheme No. 78, Vijay Nagar)
    lbl1 = "VIJAY NAGAR :  "
    txt1 = "The Hub, Scheme No. 78, Vijay Nagar, Indore"
    b_lbl1 = draw.textbbox((0, 0), lbl1, font=font_label)
    b_txt1 = draw.textbbox((0, 0), txt1, font=font_addr)
    w1_lbl = b_lbl1[2] - b_lbl1[0]
    w1_txt = b_txt1[2] - b_txt1[0]
    total_w1 = w1_lbl + w1_txt
    x1_start = (w - total_w1) / 2
    y1_row = info_y1 + 20
    draw_sparkle(draw, x1_start - 20, y1_row + 12, radius=7, color=(249, 226, 156))
    draw.text((x1_start, y1_row), lbl1, fill=(249, 226, 156), font=font_label)
    draw.text((x1_start + w1_lbl, y1_row), txt1, fill=(255, 255, 255), font=font_addr)

    # 2. SECOND ADDRESS: Rau (Opp. Bharat Petrol Pump, AB Road, Pigdamber, Rau, Indore)
    lbl2 = "RAU :  "
    txt2 = "Opp. Bharat Petrol Pump, AB Road, Pigdamber, Rau, Indore"
    b_lbl2 = draw.textbbox((0, 0), lbl2, font=font_label)
    b_txt2 = draw.textbbox((0, 0), txt2, font=font_addr)
    w2_lbl = b_lbl2[2] - b_lbl2[0]
    w2_txt = b_txt2[2] - b_txt2[0]
    total_w2 = w2_lbl + w2_txt
    x2_start = (w - total_w2) / 2
    y2_row = info_y1 + 76
    draw_sparkle(draw, x2_start - 20, y2_row + 12, radius=7, color=(249, 226, 156))
    draw.text((x2_start, y2_row), lbl2, fill=(249, 226, 156), font=font_label)
    draw.text((x2_start + w2_lbl, y2_row), txt2, fill=(250, 247, 240), font=font_addr)

    # 3. MOBILE NUMBER: 88891 77705
    phone_text = "Call / Reservation: 88891 77705"
    bbox = draw.textbbox((0, 0), phone_text, font=font_phone)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, info_y1 + 139), phone_text, fill=(250, 228, 152), font=font_phone)

    thanks_text = "Thank you for dining with us!"
    bbox = draw.textbbox((0, 0), thanks_text, font=font_thanks)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) / 2
    ty = 1692
    draw.text((tx, ty), thanks_text, fill=(247, 223, 148), font=font_thanks)

    draw_sparkle(draw, tx - 32, ty + 16, radius=11, color=(247, 223, 148))
    draw_sparkle(draw, tx + tw + 32, ty + 16, radius=11, color=(247, 223, 148))


def build_hub_standee(config, bg_img, output_filenames=["table_standee_printable.png", "standee_front_printable.png"]):
    """
    Generate the 300 DPI Primary Table Standee with reduced gap below QR code and ultra-luxury dual-outlet address box.
    """
    w, h = 1200, 1800
    canvas = bg_img.copy()
    draw = ImageDraw.Draw(canvas)
    draw_indri_luxury_borders(draw, w, h)
    draw_brand_header(canvas, draw, w)

    font_cta = get_font(46, bold=True)
    font_pill = get_font(22, bold=True)

    cta_text = "SCAN TO CONNECT"
    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 492), cta_text, fill=(255, 255, 255), font=font_cta)

    # Two Pill Badges: [G Rate Us on Google] and [Follow Us on Instagram]
    label_g = "Rate Us on Google"
    label_i = "Follow Us on Instagram"
    bbox_g = draw.textbbox((0, 0), label_g, font=font_pill)
    bbox_i = draw.textbbox((0, 0), label_i, font=font_pill)

    pill_y = 564
    pill_h = 54
    pill_w_g = (bbox_g[2] - bbox_g[0]) + 84
    pill_w_i = (bbox_i[2] - bbox_i[0]) + 84
    gap = 24
    total_pills_w = pill_w_g + gap + pill_w_i
    start_x = int((w - total_pills_w) / 2)

    # Left Pill: Rate Us on Google
    gx1, gy1 = start_x, pill_y
    gx2, gy2 = gx1 + pill_w_g, pill_y + pill_h
    draw.rounded_rectangle([gx1, gy1, gx2, gy2], radius=27, fill=(12, 18, 32), outline=(212, 175, 55), width=2)
    draw_google_g_icon(draw, gx1 + 34, gy1 + pill_h // 2, radius=13)
    draw.text((gx1 + 60, gy1 + 14), label_g, fill=(255, 255, 255), font=font_pill)

    # Right Pill: Follow Us on Instagram
    ix1, iy1 = gx2 + gap, pill_y
    ix2, iy2 = ix1 + pill_w_i, pill_y + pill_h
    draw.rounded_rectangle([ix1, iy1, ix2, iy2], radius=27, fill=(12, 18, 32), outline=(212, 175, 55), width=2)
    draw_instagram_icon(draw, ix1 + 34, iy1 + pill_h // 2, size=24)
    draw.text((ix1 + 60, iy1 + 14), label_i, fill=(255, 255, 255), font=font_pill)

    qr_url = config.get("landingPageUrl", "https://hospitalityqr.github.io/MUDOVEN-QR/?v=3")
    qr_img = generate_styled_qr(qr_url, box_size=18, border=2, fill_color=(10, 14, 24))

    card_size = 752
    qr_size = 674
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    card_x = int((w - card_size) / 2)
    card_y = 656

    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.rounded_rectangle(
        [card_x - 4, card_y + 8, card_x + card_size + 4, card_y + card_size + 16],
        radius=28,
        fill=(0, 0, 0, 140)
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=16))
    canvas_rgba = Image.alpha_composite(canvas.convert("RGBA"), shadow_layer)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_size, card_y + card_size],
        radius=26,
        fill=(255, 255, 255),
        outline=(212, 175, 55),
        width=4
    )
    canvas.paste(qr_img, (card_x + (card_size - qr_size) // 2, card_y + (card_size - qr_size) // 2))

    draw_footer(canvas, draw, w)

    for fn in output_filenames:
        canvas.save(fn, quality=95, dpi=(300, 300))
        print(f"[OK] Generated {fn} (300 DPI)")


def build_dual_direct_standee(config, bg_img, output_filename="standee_dual_direct_static.png"):
    """
    Generate 300 DPI Dual Direct Static Standee with ultra-luxury dual-outlet address box.
    """
    w, h = 1200, 1800
    canvas = bg_img.copy()
    draw = ImageDraw.Draw(canvas)
    draw_indri_luxury_borders(draw, w, h)
    draw_brand_header(canvas, draw, w)

    font_cta = get_font(42, bold=True)
    font_sub_cta = get_font(23, bold=True)
    font_card_head_g = get_font(23, bold=True)
    font_card_head_i = get_font(21, bold=True)
    font_card_sub = get_font(20, bold=True)
    font_feature_title = get_font(23, bold=True)
    font_feature_item = get_font(21, bold=False)

    cta_text = "SCAN TO CONNECT DIRECTLY"
    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 486), cta_text, fill=(255, 255, 255), font=font_cta)

    sub_cta = "Point Your Camera Directly At Either QR Below  •  Instant Open"
    bbox = draw.textbbox((0, 0), sub_cta, font=font_sub_cta)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 542), sub_cta, fill=(247, 223, 148), font=font_sub_cta)

    google_url = config.get("googleReviewUrl", "https://www.google.com/gasearch?q=mudoven%20reviews&source=sh/x/gs/m2/5#ebo=3")
    insta_url = config.get("instagramUrl", "https://www.instagram.com/mudoven_indore?stkn=MTl0c2Q4eWVueXkwNg==")

    qr_g = generate_styled_qr(google_url, box_size=14, border=2, fill_color=(10, 14, 24)).resize((404, 404), Image.Resampling.LANCZOS)
    qr_i = generate_styled_qr(insta_url, box_size=14, border=2, fill_color=(10, 14, 24)).resize((404, 404), Image.Resampling.LANCZOS)

    card_w, card_h = 475, 572
    left_x = 100
    right_x = w - 100 - card_w
    cards_y = 604

    # Left Card: Rate Us on Google
    draw.rounded_rectangle([left_x, cards_y, left_x + card_w, cards_y + card_h], radius=24, fill=(255, 255, 255), outline=(212, 175, 55), width=4)
    draw.rounded_rectangle([left_x + 22, cards_y + 18, left_x + card_w - 22, cards_y + 72], radius=27, fill=(12, 18, 32), outline=(212, 175, 55), width=2)
    draw_google_g_icon(draw, left_x + 56, cards_y + 45, radius=13)
    draw.text((left_x + 84, cards_y + 32), "Rate Us on Google", fill=(255, 255, 255), font=font_card_head_g)
    canvas.paste(qr_g, (left_x + (card_w - 404) // 2, cards_y + 88))
    draw_5_stars_row(draw, left_x + 76, cards_y + 522, star_radius=8, spacing=20, color=(218, 165, 32))
    draw.text((left_x + 182, cards_y + 511), "RATE US ON GOOGLE", fill=(12, 18, 32), font=font_card_sub)

    # Right Card: Follow Us on Instagram
    draw.rounded_rectangle([right_x, cards_y, right_x + card_w, cards_y + card_h], radius=24, fill=(255, 255, 255), outline=(212, 175, 55), width=4)
    draw.rounded_rectangle([right_x + 22, cards_y + 18, right_x + card_w - 22, cards_y + 72], radius=27, fill=(12, 18, 32), outline=(212, 175, 55), width=2)
    draw_instagram_icon(draw, right_x + 54, cards_y + 45, size=24)
    draw.text((right_x + 80, cards_y + 33), "Follow Us on Instagram", fill=(255, 255, 255), font=font_card_head_i)
    canvas.paste(qr_i, (right_x + (card_w - 404) // 2, cards_y + 88))
    i_foot = "FOLLOW @MUDOVEN_INDORE"
    bbox = draw.textbbox((0, 0), i_foot, font=font_card_sub)
    draw.text((right_x + (card_w - (bbox[2] - bbox[0])) / 2, cards_y + 511), i_foot, fill=(12, 18, 32), font=font_card_sub)

    # Luxury Hospitality Highlights Strip
    feat_x1, feat_y1 = 82, 1218
    feat_x2, feat_y2 = w - 82, 1412
    glass = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glass)
    gdraw.rounded_rectangle([feat_x1, feat_y1, feat_x2, feat_y2], radius=16, fill=(9, 13, 24, 225), outline=(212, 175, 55, 255), width=2)
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), glass).convert("RGB"))
    draw = ImageDraw.Draw(canvas)

    ft_head = "PIZZA TODAY SALAD TOMORROW  •  MUDOVEN CAFE  •  EST. 2012"
    bbox = draw.textbbox((0, 0), ft_head, font=font_feature_title)
    ft_w = bbox[2] - bbox[0]
    ft_x = (w - ft_w) / 2
    draw.text((ft_x, feat_y1 + 22), ft_head, fill=(247, 223, 148), font=font_feature_title)
    draw_sparkle(draw, ft_x - 28, feat_y1 + 35, radius=10, color=(247, 223, 148))
    draw_sparkle(draw, ft_x + ft_w + 28, feat_y1 + 35, radius=10, color=(247, 223, 148))

    ft_line1 = "Wood-Fired Pizzas  •  Artisanal Coffee  •  Global Cafe & Fine Dining"
    bbox = draw.textbbox((0, 0), ft_line1, font=font_feature_item)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, feat_y1 + 74), ft_line1, fill=(255, 255, 255), font=font_feature_item)

    ft_line2 = "\"We Speak The Good Food Language\"  —  Your Forever Happy Place!"
    bbox = draw.textbbox((0, 0), ft_line2, font=font_feature_item)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, feat_y1 + 120), ft_line2, fill=(226, 232, 240), font=font_feature_item)

    draw_footer(canvas, draw, w)
    canvas.save(output_filename, quality=95, dpi=(300, 300))
    print(f"[OK] Generated {output_filename} (300 DPI)")


def build_single_direct_standee(config, bg_img, url, mode="google", output_filename="standee_google_direct.png"):
    """
    Generate 300 DPI Single Direct Standee with reduced gap below QR code and ultra-luxury dual-outlet address box.
    """
    w, h = 1200, 1800
    canvas = bg_img.copy()
    draw = ImageDraw.Draw(canvas)
    draw_indri_luxury_borders(draw, w, h)
    draw_brand_header(canvas, draw, w)

    font_cta = get_font(44, bold=True)
    font_pill = get_font(24, bold=True)

    if mode == "google":
        cta_text = "RATE US ON GOOGLE"
        pill_label = "Rate Us on Google  •  5-Star Rating"
    else:
        cta_text = "FOLLOW US ON INSTAGRAM"
        pill_label = "Follow Us on Instagram  •  @mudoven_indore"

    bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
    draw.text(((w - (bbox[2] - bbox[0])) / 2, 492), cta_text, fill=(255, 255, 255), font=font_cta)

    bbox_p = draw.textbbox((0, 0), pill_label, font=font_pill)
    pill_w = (bbox_p[2] - bbox_p[0]) + 96
    pill_h = 54
    px1 = int((w - pill_w) / 2)
    py1 = 564
    draw.rounded_rectangle([px1, py1, px1 + pill_w, py1 + pill_h], radius=27, fill=(12, 18, 32), outline=(212, 175, 55), width=2)
    if mode == "google":
        draw_google_g_icon(draw, px1 + 38, py1 + pill_h // 2, radius=14)
    else:
        draw_instagram_icon(draw, px1 + 38, py1 + pill_h // 2, size=26)
    draw.text((px1 + 70, py1 + 13), pill_label, fill=(255, 255, 255), font=font_pill)

    qr_img = generate_styled_qr(url, box_size=18, border=2, fill_color=(10, 14, 24))
    card_size = 752
    qr_size = 674
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    card_x = int((w - card_size) / 2)
    card_y = 656

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_size, card_y + card_size],
        radius=26,
        fill=(255, 255, 255),
        outline=(212, 175, 55),
        width=4
    )
    canvas.paste(qr_img, (card_x + (card_size - qr_size) // 2, card_y + (card_size - qr_size) // 2))

    draw_footer(canvas, draw, w)
    canvas.save(output_filename, quality=95, dpi=(300, 300))
    print(f"[OK] Generated {output_filename} (300 DPI)")


def build_mobile_landing_preview(bg_img, output_filename="mobile_landing_preview.png"):
    """
    Generate a visual preview of the Mobile QR Landing Page (index.html) with:
    - Compact Brand Header & Generous Center Breathing Space
    - 'Rate Us on Google' and 'Follow Us on Instagram' interactive cards
    - Ambience gallery strip where the 2nd photo clearly showcases the top 'MUDOVEN' neon sign
    - Ultra-Luxury Dual-Outlet Address Box (Vijay Nagar First, then Rau) + Mobile 88891 77705
    """
    w, h = 1200, 1800
    canvas = bg_img.copy()
    draw = ImageDraw.Draw(canvas)
    draw_indri_luxury_borders(draw, w, h)
    draw_brand_header(canvas, draw, w)

    font_card_title = get_font(32, bold=True)
    font_card_desc = get_font(23, bold=False)
    font_card_tag = get_font(22, bold=True)
    font_sec = get_font(22, bold=True)

    glass = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glass)
    c1_y1, c1_y2 = 496, 702
    c2_y1, c2_y2 = 738, 944
    gdraw.rounded_rectangle([115, c1_y1, w - 115, c1_y2], radius=24, fill=(18, 22, 34, 236), outline=(247, 223, 148, 255), width=3)
    gdraw.rounded_rectangle([115, c2_y1, w - 115, c2_y2], radius=24, fill=(10, 15, 26, 232), outline=(212, 175, 55, 230), width=2)
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), glass).convert("RGB"))
    draw = ImageDraw.Draw(canvas)

    # Google Card Content
    draw.rounded_rectangle([150, c1_y1 + 44, 265, c1_y1 + 159], radius=24, fill=(255, 255, 255), outline=(212, 175, 55), width=2)
    draw_google_g_icon(draw, 207, c1_y1 + 101, radius=34)
    draw.text((300, c1_y1 + 38), "Rate Us on Google", fill=(255, 255, 255), font=font_card_title)
    draw.text((300, c1_y1 + 86), "Share your dining experience with us", fill=(203, 213, 225), font=font_card_desc)
    draw_5_stars_row(draw, 310, c1_y1 + 143, star_radius=10, spacing=26, color=(251, 191, 36))
    draw.text((445, c1_y1 + 131), "Tap to Review", fill=(247, 223, 148), font=font_card_tag)
    ax1, ay1 = w - 183, c1_y1 + 103
    draw.ellipse([ax1 - 32, ay1 - 32, ax1 + 32, ay1 + 32], fill=(212, 175, 55), outline=(247, 223, 148), width=2)
    draw.line([ax1 - 12, ay1, ax1 + 10, ay1], fill=(9, 13, 24), width=3)
    draw.line([ax1 + 2, ay1 - 9, ax1 + 11, ay1], fill=(9, 13, 24), width=3)
    draw.line([ax1 + 2, ay1 + 9, ax1 + 11, ay1], fill=(9, 13, 24), width=3)

    # Instagram Card Content
    draw.rounded_rectangle([150, c2_y1 + 44, 265, c2_y1 + 159], radius=24, fill=(214, 41, 118), outline=(247, 223, 148), width=2)
    draw_instagram_icon(draw, 207, c2_y1 + 101, size=64)
    draw.text((300, c2_y1 + 38), "Follow Us on Instagram", fill=(255, 255, 255), font=font_card_title)
    draw.text((300, c2_y1 + 86), "Explore wood-fired pizzas, reels & happy vibes", fill=(203, 213, 225), font=font_card_desc)
    draw.text((300, c2_y1 + 131), "@mudoven_indore", fill=(247, 223, 148), font=font_card_tag)
    ax2, ay2 = w - 183, c2_y1 + 103
    draw.ellipse([ax2 - 32, ay2 - 32, ax2 + 32, ay2 + 32], fill=(16, 24, 42), outline=(212, 175, 55), width=2)
    draw.line([ax2 - 12, ay2, ax2 + 10, ay2], fill=(247, 223, 148), width=3)
    draw.line([ax2 + 2, ay2 - 9, ax2 + 11, ay2], fill=(247, 223, 148), width=3)
    draw.line([ax2 + 2, ay2 + 9, ax2 + 11, ay2], fill=(247, 223, 148), width=3)

    # Ambience Showcase Strip
    sec_label = "PIZZA TODAY SALAD TOMORROW  •  MUDOVEN"
    bbox = draw.textbbox((0, 0), sec_label, font=font_sec)
    sw = bbox[2] - bbox[0]
    sx = (w - sw) / 2
    draw.text((sx, 1004), sec_label, fill=(247, 223, 148), font=font_sec)
    draw_sparkle(draw, sx - 24, 1017, radius=9, color=(247, 223, 148))
    draw_sparkle(draw, sx + sw + 24, 1017, radius=9, color=(247, 223, 148))

    thumb_w, thumb_h = 302, 354
    thumb_gap = 32
    t_start_x = int((w - (thumb_w * 3 + thumb_gap * 2)) / 2)
    t_y = 1054
    for idx, fn in enumerate(["ambience_1.jpg", "ambience_2.jpg", "ambience_3.jpg"]):
        tx = t_start_x + idx * (thumb_w + thumb_gap)
        if os.path.exists(fn):
            im = Image.open(fn).convert("RGB")
            iw, ih = im.size
            s_r = iw / ih
            t_r = thumb_w / thumb_h
            if s_r > t_r:
                nw = int(ih * t_r)
                # For ambience_2.jpg, bias horizontal crop toward right where 'MUDOVEN' neon sign sits
                if idx == 1:
                    left = max(0, min(iw - nw, int(iw * 0.60 - nw / 2)))
                else:
                    left = (iw - nw) // 2
                im = im.crop((left, 0, left + nw, ih))
            else:
                nh = int(iw / t_r)
                # Keep top aligned for ambience_2.jpg so top 'MUDOVEN' sign is 100% visible
                top = 0 if idx == 1 else (ih - nh) // 2
                im = im.crop((0, top, iw, top + nh))
            im = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            canvas.paste(im, (tx, t_y))
            draw.rounded_rectangle([tx, t_y, tx + thumb_w, t_y + thumb_h], radius=16, outline=(212, 175, 55), width=3)

    draw_footer(canvas, draw, w)
    canvas.save(output_filename, quality=95)
    print(f"[OK] Generated {output_filename}")


def main():
    print("Preparing Mudoven brand logos and architectural photos...")
    prepare_brand_assets()

    config = load_config("config.js")
    landing_url = config.get("landingPageUrl", "https://hospitalityqr.github.io/mudoven-google-instagram-qr/?v=1")
    google_url = config.get("googleReviewUrl", "https://www.google.com/gasearch?q=mudoven%20reviews&source=sh/x/gs/m2/5#ebo=3")
    insta_url = config.get("instagramUrl", "https://www.instagram.com/mudoven_indore?stkn=MTl0c2Q4eWVueXkwNg==")

    print("Generating shared Mudoven Luxury Ambience Background...")
    bg_img = create_ambience_luxury_background(1200, 1800)
    bg_img.save("bg_ambience_luxury.jpg", quality=93)
    print("[OK] Saved bg_ambience_luxury.jpg")

    print("Generating standalone high-res QR codes...")
    qr_hub = generate_styled_qr(landing_url, box_size=18, border=2, fill_color=(10, 14, 24))
    qr_hub.save("qr_code.png")
    qr_hub.save("qr_landing_page.png")

    qr_google = generate_styled_qr(google_url, box_size=18, border=2, fill_color=(10, 14, 24))
    qr_google.save("qr_google_direct.png")

    qr_insta = generate_styled_qr(insta_url, box_size=18, border=2, fill_color=(10, 14, 24))
    qr_insta.save("qr_instagram_direct.png")
    print("[OK] Generated qr_code.png, qr_landing_page.png, qr_google_direct.png, qr_instagram_direct.png")

    build_hub_standee(config, bg_img, ["table_standee_printable.png", "standee_front_printable.png"])
    build_dual_direct_standee(config, bg_img, "standee_dual_direct_static.png")
    build_single_direct_standee(config, bg_img, google_url, mode="google", output_filename="standee_google_direct.png")
    build_single_direct_standee(config, bg_img, insta_url, mode="instagram", output_filename="standee_instagram_direct.png")
    build_mobile_landing_preview(bg_img, "mobile_landing_preview.png")


if __name__ == "__main__":
    main()
