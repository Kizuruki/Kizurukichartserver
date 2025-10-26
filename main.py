if __name__ == "__main__":
    import asyncio
    from app import start_fastapi
    import argparse

    args = argparse.ArgumentParser()
    parsed_args = args.parse_args()
    asyncio.run(start_fastapi(parsed_args))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import secrets, time, os

app = FastAPI()
SESSIONS = {}

@app.post("/api/accounts/session/external/complete")
async def external_complete(request: Request):
    # trust boundary: restrict to internal calls from sonoserver
    if request.headers.get("X-Internal-Auth") != os.getenv("INTERNAL_SHARED_SECRET",""):
        raise HTTPException(403, "Forbidden")
    body = await request.json()
    user = body.get("userProfile") or {}
    user_id = user.get("id") or f"anon-{secrets.token_hex(6)}"
    name = user.get("name") or "Sonolus User"

    sid = secrets.token_urlsafe(24)
    SESSIONS[sid] = {"user_id": user_id, "name": name, "created_ms": int(time.time()*1000)}

    # If you used an externalId correlation, you could store a map extId->sid here too.
    return JSONResponse({"session": sid, "user": {"id": user_id, "name": name}})

@app.post("/api/accounts/session/external/id/")
async def external_id():
    # optional: front-end asks for an external login id used as a correlation param
    return JSONResponse({"id": secrets.token_urlsafe(12)})

@app.get("/api/accounts/session/me")
async def me(request: Request):
    auth = request.headers.get("authorization","")
    sid = auth.replace("Bearer ", "").strip()
    data = SESSIONS.get(sid)
    if not data:
        raise HTTPException(401, "No session")
    return JSONResponse({"user": {"id": data["user_id"], "name": data["name"]}})
