# sonoserver/routes/results.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# GET /sonolus/levels/result/info must advertise submits to show the button.
# Spec: exposes a non-empty "submits" array. :contentReference[oaicite:4]{index=4}
@router.get("/sonolus/levels/result/info")
async def result_info():
    return JSONResponse({
        "submits": [{
            "type": "form",
            "title": "Submit Replay",
            "fields": []  # expand later (e.g., allow note or privacy)
        }]
    })

# POST /sonolus/levels/result/submit — receive replay metadata and return {key, hashes}
# Spec: submit + upload flow from result screen. :contentReference[oaicite:5]{index=5}
@router.post("/sonolus/levels/result/submit")
async def result_submit(request: Request):
    body = await request.json()
    # TODO: validate Sonolus-Session if you require login for submissions
    # Decide which files you want uploaded, then return their hashes + an opaque key.
    # For a basic pipeline, echo requested replay hashes:
    replay = (body or {}).get("replay", {})
    hashes = (replay.get("data") or {}).get("hashes", [])
    return JSONResponse({"key": "upload-key-001", "hashes": hashes})

# POST /sonolus/levels/result/upload — receive file parts for the hashes from submit
@router.post("/sonolus/levels/result/upload")
async def result_upload(request: Request):
    # In production: parse multipart/stream, persist files by hash, finalize a score row.
    return JSONResponse({"message": "Uploaded"})
