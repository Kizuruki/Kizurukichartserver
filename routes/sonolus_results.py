from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/sonolus/levels/result/info")
async def result_info():
    return JSONResponse({
        "submits": [{
            "type": "form",
            "title": "Submit Replay",
            "fields": []
        }]
    })

@router.post("/sonolus/levels/result/submit")
async def result_submit(request: Request):
    body = await request.json()
    replay = (body or {}).get("replay", {})
    hashes = (replay.get("data") or {}).get("hashes", [])
    return JSONResponse({"key": "upload-key-001", "hashes": hashes})

@router.post("/sonolus/levels/result/upload")
async def result_upload(request: Request):
    # TODO: accept multipart, persist by hash, finalize score row
    return JSONResponse({"message": "Uploaded"})
