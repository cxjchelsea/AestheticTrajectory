from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.storage.file_storage import resolve_uploaded_file, save_upload

router = APIRouter(tags=["files"])


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        return save_upload(file.filename or "upload.bin", content, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/files/{file_id}")
def get_file(file_id: str):
    path = resolve_uploaded_file(file_id)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
