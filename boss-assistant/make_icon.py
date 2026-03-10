"""One-time script: create boss_assistant.ico for the desktop shortcut. Run: python make_icon.py"""
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / "boss_assistant.ico"
W = 32
H = 32

# ICO: 6-byte header, 16-byte directory entry, then BMP data
ico_header = struct.pack("<HHH", 0, 1, 1)
# ICONDIRENTRY: width, height, 0, 0, 1 plane, 32 bpp, image size, offset 22
bmp_header_size = 14 + 40
bmp_pixels = W * H * 4
bmp_size = bmp_header_size + bmp_pixels
ico_entry = struct.pack("<BBBBHHII", W, H, 0, 0, 1, 32, bmp_size, 22)

# BMP: 14-byte file header
bmp_file = struct.pack("<2sIHHI", b"BM", 14 + 40 + bmp_pixels, 0, 0, 54)
# 40-byte DIB header
bmp_info = struct.pack(
    "<IiiHHIIiiII", 40, W, H, 1, 32, 0, bmp_pixels, 0, 0, 0, 0
)
# Pixels: bottom-up, BGRx. Gold/amber accent (#c9a227) on dark (#1a1a1a)
dark = (0x1a, 0x1a, 0x1a, 255)
gold = (0x27, 0xa2, 0xc9, 255)  # BGR
pixels = []
for y in range(H - 1, -1, -1):
    for x in range(W):
        # Simple: rounded rect in center = gold, else dark
        cx, cy = W / 2 - 0.5, H / 2 - 0.5
        dx, dy = (x - cx) / (W * 0.35), (y - cy) / (H * 0.35)
        if dx * dx + dy * dy <= 1.0:
            pixels.append(gold)
        else:
            pixels.append(dark)
pixel_data = b"".join(struct.pack("BBBB", *p) for p in pixels)

with open(OUT, "wb") as f:
    f.write(ico_header)
    f.write(ico_entry)
    f.write(bmp_file)
    f.write(bmp_info)
    f.write(pixel_data)
print("Created:", OUT)
