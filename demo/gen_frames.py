#!/usr/bin/env python3
"""Generate demo video frames for VoiceMate ID."""

import json, subprocess, os
from PIL import Image, ImageDraw, ImageFont

OUT = "/home/hikahermes/voicemate-id/demo"
W, H = 1080, 1920

BG = (22, 28, 36)
MSG_USER_BG = (56, 120, 180)
MSG_BOT_BG = (42, 47, 55)
WHITE = (255, 255, 255)
GRAY = (150, 160, 170)
ACCENT = (0, 180, 120)
TOPBAR = (30, 36, 44)

with open(f"{OUT}/conversation.json") as f:
    conv = json.load(f)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_voice_bubble(draw, x, y, width, is_user, duration="0:06"):
    bg = MSG_USER_BG if is_user else MSG_BOT_BG
    draw.rounded_rectangle((x, y, x+width, y+80), radius=20, fill=bg)
    icon_x, icon_y = x + 20, y + 25
    draw.ellipse((icon_x, icon_y, icon_x+30, icon_y+30), fill=WHITE if is_user else ACCENT)
    for i in range(12):
        bar_h = 8 + (i % 5) * 6
        bx = icon_x + 50 + i * 14
        by = icon_y + 15 - bar_h // 2
        color = WHITE if is_user else (100, 200, 160)
        draw.rectangle((bx, by, bx + 8, by + bar_h), fill=color)
    dur_font = get_font(22)
    draw.text((x + width - 80, y + 50), duration, fill=(200,200,220) if is_user else GRAY, font=dur_font)

def wrap_text(text, font, max_width, draw):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines

# ---- Frame 1: Title ----
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)
cx, cy = W//2, H//2 - 200
draw.ellipse((cx-80, cy-80, cx+80, cy+80), fill=ACCENT)
draw.text((cx, cy), "VM", fill=WHITE, font=get_font(60, True), anchor="mm")
draw.text((W//2, cy+140), "VoiceMate ID", fill=WHITE, font=get_font(72, True), anchor="mm")
draw.text((W//2, cy+210), "Indonesian Voice AI Assistant", fill=GRAY, font=get_font(36), anchor="mm")
draw.text((W//2, cy+270), "Powered by Xiaomi MiMo", fill=ACCENT, font=get_font(28), anchor="mm")
for i, badge in enumerate(["mimo-v2-omni (STT)", "mimo-v2.5-pro (Reasoning)", "mimo-v2.5-tts (Voice)"]):
    by = cy + 330 + i * 50
    draw.rounded_rectangle((W//2-200, by, W//2+200, by+36), radius=18, fill=(30, 40, 50))
    draw.text((W//2, by+18), badge, fill=ACCENT, font=get_font(24), anchor="mm")
img.save(f"{OUT}/frame_title.png")

# ---- Frame 2: User sent voice ----
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, W, 120), fill=TOPBAR)
draw.text((30, 50), "<", fill=ACCENT, font=get_font(40), anchor="lm")
draw.text((100, 40), "VoiceMate ID", fill=WHITE, font=get_font(36, True))
draw.text((100, 75), "online", fill=ACCENT, font=get_font(24))

chat_y = 160
draw.text((W//2, chat_y), "Today 09:53", fill=GRAY, font=get_font(22), anchor="mm")
chat_y += 50

bubble_w = 500
bubble_x = W - bubble_w - 40
draw_voice_bubble(draw, bubble_x, chat_y, bubble_w, True, "0:06")
text_y = chat_y + 95
msg_font = get_font(30)
for line in wrap_text(conv["user"], msg_font, bubble_w - 40, draw):
    draw.text((bubble_x + 20, text_y), line, fill=WHITE, font=msg_font)
    text_y += 40
draw.text((bubble_x + bubble_w - 40, text_y), "✓✓", fill=(130, 200, 255), font=get_font(22))

# Typing indicator
typing_y = text_y + 60
draw.rounded_rectangle((40, typing_y, 180, typing_y+40), radius=20, fill=MSG_BOT_BG)
for i in range(3):
    draw.ellipse((60+i*35, typing_y+12, 75+i*35, typing_y+27), fill=GRAY)
draw.text((190, typing_y+10), "VoiceMate is thinking...", fill=GRAY, font=get_font(20))
img.save(f"{OUT}/frame_thinking.png")

# ---- Frame 3: Full chat ----
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)
draw.rectangle((0, 0, W, 120), fill=TOPBAR)
draw.text((30, 50), "<", fill=ACCENT, font=get_font(40), anchor="lm")
draw.text((100, 40), "VoiceMate ID", fill=WHITE, font=get_font(36, True))
draw.text((100, 75), "online", fill=ACCENT, font=get_font(24))

chat_y = 160
draw.text((W//2, chat_y), "Today 09:53", fill=GRAY, font=get_font(22), anchor="mm")
chat_y += 50

# User msg
draw_voice_bubble(draw, bubble_x, chat_y, bubble_w, True, "0:06")
text_y = chat_y + 95
for line in wrap_text(conv["user"], msg_font, bubble_w - 40, draw):
    draw.text((bubble_x + 20, text_y), line, fill=WHITE, font=msg_font)
    text_y += 40
draw.text((bubble_x + bubble_w - 40, text_y), "✓✓", fill=(130, 200, 255), font=get_font(22))

# Bot reply
bot_y = text_y + 40
bot_bubble_w = 550
draw.text((40, bot_y - 25), "VoiceMate ID", fill=ACCENT, font=get_font(22))
draw_voice_bubble(draw, 40, bot_y, bot_bubble_w, False, "0:13")
bot_text_y = bot_y + 95
for line in wrap_text(conv["bot"], msg_font, bot_bubble_w - 40, draw):
    draw.text((60, bot_text_y), line, fill=WHITE, font=msg_font)
    bot_text_y += 40

# Bottom bar
draw.rectangle((0, H-100, W, H), fill=TOPBAR)
draw.rounded_rectangle((20, H-80, W-80, H-20), radius=25, fill=(40, 46, 56))
draw.text((40, H-60), "Hold to record voice...", fill=GRAY, font=get_font(28))
img.save(f"{OUT}/frame_chat.png")

print("All 3 frames generated!")
