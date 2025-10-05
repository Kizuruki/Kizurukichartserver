# helpers/pjsk_background_gen_PIL.py
"""
Compatibility shim for pjsk background generator.
Tries to import known package names and map their API to `render_v3(jacket)`.
If no real package is found, provides a Pillow-based fallback implementation.
"""

from PIL import Image, ImageFilter, ImageOps
import importlib

_real = None
_real_render_fn = None

# Candidate package/module names to try (common variants)
_candidates = [
    "pjsk_background_gen_PIL",
    "pjsekai_background_gen_pillow",
    "pjsekai_background_gen_pil",
    "pjsk_bg",
    "pjsk_background_gen",
    "pjsk_background",
]

for cand in _candidates:
    try:
        mod = importlib.import_module(cand)
        _real = mod
        break
    except Exception:
        _real = None

# helper to locate a render-like function on the real module
def _find_render_fn(mod):
    if not mod:
        return None
    # common names
    for name in ("render_v3", "render", "generate_background", "render_bg"):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    # some modules export a class; try common attribute names
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if callable(obj) and attr.lower().startswith("render"):
            return obj
    return None

if _real:
    _real_render_fn = _find_render_fn(_real)

# Fallback Pillow-based implementation (used if no real module found)
def _fallback_render_v3(jacket: Image.Image, out_size=(1280, 720)) -> Image.Image:
    jacket = jacket.convert("RGBA")
    w, h = out_size
    scale = max(w / jacket.width, h / jacket.height) * 1.5
    bg_w = int(jacket.width * scale)
    bg_h = int(jacket.height * scale)
    bg = jacket.resize((bg_w, bg_h), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    left = (bg_w - w) // 2
    top = (bg_h - h) // 2
    bg = bg.crop((left, top, left + w, top + h))
    jacket_small = jacket.copy().resize((int(w * 0.5), int(h * 0.5)), Image.LANCZOS)
    overlay = Image.new("RGBA", (w, h))
    overlay.paste(jacket_small, ((w - jacket_small.width) // 2, (h - jacket_small.height) // 2), jacket_small)
    # dim overlay
    alpha = overlay.split()[-1].point(lambda p: p * 0.7)
    overlay.putalpha(alpha)
    bg = bg.convert("RGBA")
    try:
        result = Image.alpha_composite(bg, overlay)
    except Exception:
        # if sizes/modes mismatch, place overlay manually
        bg.paste(overlay, (0, 0), overlay)
        result = bg
    return result

# Public function used by the project
def render_v3(jacket: Image.Image, *args, **kwargs) -> Image.Image:
    """
    Unified API for the project's expectation: render_v3(jacket) -> PIL.Image
    If a real implementation was found, call it (and adapt signature if necessary).
    Otherwise use local fallback.
    """
    # if real module + function exists, try calling it
    if _real and _real_render_fn:
        try:
            # try calling with the expected signature first
            return _real_render_fn(jacket, *args, **kwargs)
        except TypeError:
            # try calling with only jacket
            try:
                return _real_render_fn(jacket)
            except Exception:
                pass
        except Exception:
            # If real module fails for some reason, fallback gracefully
            pass

    # fallback
    return _fallback_render_v3(jacket, *args, **kwargs)


# Expose module-level names just like original module likely did
__all__ = ["render_v3"]
