"""Shared helpers: rectify Norrtvätt's box from the Shopify photo and paste it into ad images."""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Box corners in the Shopify "box in hand" photo (TL, TR, BR, BL): front face + thin top/right slivers.
SRC_QUAD = np.float32([[243.5, 128.0], [780.5, 126.0], [780.5, 710.5], [243.5, 699.0]])
TEX_W, TEX_H = 540, 578  # aspect 0.934


def box_texture(path, scale=2):
    """The user's box as a flat, upright RGB texture (scale x the native size)."""
    src = cv2.cvtColor(np.asarray(Image.open(path).convert("RGB")), cv2.COLOR_RGB2BGR)
    w, h = TEX_W * scale, TEX_H * scale
    M = cv2.getPerspectiveTransform(SRC_QUAD, np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
    tex = cv2.warpPerspective(src, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return cv2.cvtColor(tex, cv2.COLOR_BGR2RGB).astype(np.float32)


def warp_to_quad(tex, quad, size, ss=3):
    """Warp texture onto quad (TL,TR,BR,BL) in an image of `size` (W,H); returns rgb, alpha (0..1).
    Rendered at ss x and downsampled so the edges are anti-aliased."""
    W, H = size
    th, tw = tex.shape[:2]
    q = np.float32(quad) * ss
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]), q)
    rgb = cv2.warpPerspective(tex, M, (W * ss, H * ss), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    al = cv2.warpPerspective(np.ones((th, tw), np.float32), M, (W * ss, H * ss), flags=cv2.INTER_LINEAR)
    rgb = cv2.resize(rgb * al[..., None], (W, H), interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, (W, H), interpolation=cv2.INTER_AREA)
    rgb = np.where(al[..., None] > 1e-4, rgb / np.maximum(al[..., None], 1e-4), 0)
    return rgb, np.clip(al, 0, 1)


def quad_from_plane(old_quad, u0, u1, v0, v1):
    """old_quad maps the unit square (u,v in 0..1) of a box face; return the quad covering u0..u1, v0..v1
    of that same plane (used to make the box taller/wider along its own edges, perspective kept)."""
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), np.float32(old_quad))
    pts = np.float32([[[u0, v0]], [[u1, v0]], [[u1, v1]], [[u0, v1]]])
    return cv2.perspectiveTransform(pts, M).reshape(4, 2)


def over(base, rgb, alpha):
    """Alpha-composite rgb over base (float arrays)."""
    return base * (1 - alpha[..., None]) + rgb * alpha[..., None]


def font_for_cap(path, cap, text="H"):
    f = ImageFont.truetype(path, 200)
    b = f.getbbox(text)
    return ImageFont.truetype(path, max(1, round(200 * cap / (b[3] - b[1]))))


def fit_font(path, cap, s, max_w):
    f = font_for_cap(path, cap)
    while f.getlength(s) > max_w and f.size > 6:
        f = ImageFont.truetype(path, f.size - 1)
    return f


def inpaint(img_u8, mask_u8, r=5):
    """OpenCV Telea inpaint on an RGB uint8 array."""
    return cv2.inpaint(img_u8, mask_u8, r, cv2.INPAINT_TELEA)
