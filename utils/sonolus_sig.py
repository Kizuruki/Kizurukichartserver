import base64, time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

_SONOLUS_JWK = {
    "kty": "EC",
    "crv": "P-256",
    "x": "d2B14ZAn-zDsqY42rHofst8rw3XB90-a5lT80NFdXo0",
    "y": "Hxzi9DHrlJ4CVSJVRnydxFWBZAgkFxZXbyxPSa8SJQw",
}

def _b64u_decode(s: str) -> bytes:
    s += "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def _pubkey():
    x = int.from_bytes(_b64u_decode(_SONOLUS_JWK["x"]), "big")
    y = int.from_bytes(_b64u_decode(_SONOLUS_JWK["y"]), "big")
    nums = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
    return nums.public_key()

_PUB = _pubkey()

def verify_sonolus_signature(raw_body: bytes, sig_b64u: str | None) -> bool:
    if not sig_b64u:
        return False
    try:
        sig = _b64u_decode(sig_b64u)
        half = len(sig) // 2
        if half * 2 == len(sig):
            # raw r||s -> DER
            r = int.from_bytes(sig[:half], "big")
            s = int.from_bytes(sig[half:], "big")
            sig = encode_dss_signature(r, s)
        _PUB.verify(sig, raw_body, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def is_recent(ts_ms: int, skew_ms: int = 5 * 60 * 1000) -> bool:
    now = int(time.time() * 1000)
    try:
        ts = int(ts_ms or 0)
    except Exception:
        return False
    return abs(now - ts) <= skew_ms
