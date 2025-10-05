# pjsk_background_gen_PIL.py
"""
Compatibility bridge so code that does `import pjsk_background_gen_PIL`
can find the implementation living at helpers/pjsk_background_gen_PIL.py.

Priority:
 1. Try to import a real installed package under common names.
 2. Fall back to helpers/pjsk_background_gen_PIL (your local shim).
"""

import importlib

_candidates = [
    "pjsk_background_gen_PIL",
    "pjsekai_background_gen_pillow",
    "pjsekai_background_gen_pil",
    "pjsk_bg",
    "pjsk_background_gen",
    "pjsk_background",
]

_loaded = None
for name in _candidates:
    try:
        _loaded = importlib.import_module(name)
        break
    except Exception:
        _loaded = None

if _loaded is None:
    # Use local helper shim inside helpers/
    try:
        from helpers.pjsk_background_gen_PIL import *  # noqa: F401,F403
    except Exception as e:
        # Last-resort: raise an informative ImportError so startup log is clearer
        raise ImportError(
            "Could not import pjsk_background_gen_PIL. "
            "Tried installed packages and helpers/pjsk_background_gen_PIL.py. "
            f"Last error: {e}"
        )
else:
    # Re-export everything from the loaded module for compatibility
    globals().update({k: getattr(_loaded, k) for k in dir(_loaded) if not k.startswith("_")})
