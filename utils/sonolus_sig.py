# sonoserver/utils/sonolus_sig.py
import base64, json, time
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

# Public JWK from the Sonolus spec (P-256)
# Spec: Sonolus-Signature uses ECDSA-SHA256 and this public JWK. :contentReference[oaicite:1]{index=1}
_SONOLUS_JWK = {
    "kty": "EC",
    "crv": "P-256",
    "x": "d2B14ZAn-zDsqY42rHofst8rw3XB90-a5lT80NFdXo0",
    "y": "Hxzi9DHrlJ4CVSJVRnydxFWBZAgkFxZXbyxPSa8SJQw",
}

def _b64u_decode(s: str) -> bytes:
    s = s + "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s.encode())

def _pubkey_from_jwk(jwk: dict) -> ec.EllipticCurvePublicKey:
    x = int.from_bytes(_b64u_decode(jwk["x"]), "big")
    y = int.from_bytes(_b64u_decode(jwk["y"]), "big")
    numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
    return numbers.public_key()

_PUB = _pubkey_from_jwk(_SONOLUS_JWK)

def verify_sonolus_signature(raw_body: bytes, sig_b64u: Optional[str]) -> bool:
    if not sig_b64u:
        return False
    try:
        sig = _b64u_decode(sig_b64u)
        # If the signature is r||s, convert to DER; if already DER, verification will pass as-is.
        half = len(sig) // 2
        try_raw_rs = half * 2 == len(sig)
        if try_raw_rs:
            r = int.from_bytes(sig[:half], "big")
            s = int.from_bytes(sig[half:], "big")
            sig = encode_dss_signature(r, s)
        _PUB.verify(sig, raw_body, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def is_recent(ts_ms: int, skew_ms: int = 5 * 60 * 1000) -> bool:
    return abs(int(time.time() * 1000) - int(ts_ms or 0)) <= skew_ms
