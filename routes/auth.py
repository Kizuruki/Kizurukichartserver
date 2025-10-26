# sonoserver/routes/auth.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json, time, os
from utils.sonolus_sig import verify_sonolus_signature, is_recent

router = APIRouter()

# POST /sonolus/authenticate_external — “Sign in with Sonolus” callback
# Spec: External Authentication (deep link → POST to your endpoint). :contentReference[oaicite:2]{index=2}
@router.post("/sonolus/authenticate_external")
async def authenticate_external(request: Request):
    raw = await request.body()
    sig = request.headers.get("Sonolus-Signature")
    if not verify_sonolus_signature(raw, sig):
        raise HTTPException(401, "Invalid signature")
    body = json.loads(raw.decode("utf-8"))

    if body.get("type") != "authenticateExternal":
        raise HTTPException(401, "Invalid type")
    if not is_recent(body.get("time", 0)):
        raise HTTPException(401, "Stale message")

    # Minimal profile fields (examples; body.userProfile may include more)
    profile = body.get("userProfile", {})
    sonolus_user_id = profile.get("id")
    name = profile.get("name")

    # Call your chart-backend to mint a WEBSITE session for charts.kizuruki.com
    # (Or write directly to a shared DB/session store.)
    # Example: POST http://127.0.0.1:8080/api/accounts/session/external/complete
    # with the signed body so backend can trust it (in production, use an internal secret).
    # For this skeleton, we just return a message that the website can poll for status.
    return JSONResponse({"message": f"Logged in as {name or 'Sonolus User'}."})

# POST /sonolus/authenticate — optional short-lived session for privileged Sonolus calls
# Spec: POST /sonolus/authenticate returns { session, expiration }. :contentReference[oaicite:3]{index=3}
@router.post("/sonolus/authenticate")
async def authenticate_app(request: Request):
    raw = await request.body()
    sig = request.headers.get("Sonolus-Signature")
    if not verify_sonolus_signature(raw, sig):
        raise HTTPException(401, "Invalid signature")
    body = json.loads(raw.decode("utf-8"))
    if not is_recent(body.get("time", 0)):
        raise HTTPException(401, "Stale message")

    # Create a short-lived token the app will echo back on privileged calls
    exp_ms = int(time.time() * 1000) + 30 * 60 * 1000  # 30 minutes
    return JSONResponse({"session": "sonolus-session-token", "expiration": exp_ms})
