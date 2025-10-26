from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json, time, os, httpx
from utils.sonolus_sig import verify_sonolus_signature, is_recent

router = APIRouter()

# POST /sonolus/authenticate_external
@router.post("/sonolus/authenticate_external")
async def authenticate_external(request: Request):
    raw = await request.body()
    sig = request.headers.get("Sonolus-Signature")
    if not verify_sonolus_signature(raw, sig):
        raise HTTPException(401, "Invalid signature")

    body = json.loads(raw.decode())
    if body.get("type") != "authenticateExternal":
        raise HTTPException(401, "Invalid type")
    if not is_recent(body.get("time", 0)):
        raise HTTPException(401, "Stale")

    user_profile = body.get("userProfile", {})  # { id, name, ... }
    # Optional: match external-login correlation id (?id=...) if you pass it through your deep link
    external_id = request.query_params.get("id")

    # Call chart-backend to mint website session (internal call)
    backend_url = os.getenv("CHART_BACKEND_URL", "http://127.0.0.1:8080")
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(
            f"{backend_url}/api/accounts/session/external/complete",
            json={"userProfile": user_profile, "externalId": external_id},
            headers={"X-Internal-Auth": os.getenv("INTERNAL_SHARED_SECRET","")}
        )
    if r.status_code != 200:
        raise HTTPException(500, "Session creation failed")

    # Sonolus expects a ServerMessage; your website will poll/check session
    return JSONResponse({"message": f"Logged in as {user_profile.get('name','Sonolus User')}."})

# POST /sonolus/authenticate  (short-lived token for privileged Sonolus calls)
@router.post("/sonolus/authenticate")
async def authenticate(request: Request):
    raw = await request.body()
    sig = request.headers.get("Sonolus-Signature")
    if not verify_sonolus_signature(raw, sig):
        raise HTTPException(401, "Invalid signature")
    body = json.loads(raw.decode())
    if not is_recent(body.get("time", 0)):
        raise HTTPException(401, "Stale")
    exp = int(time.time() * 1000) + 30 * 60 * 1000
    return JSONResponse({"session": "sonolus-session-token", "expiration": exp})
