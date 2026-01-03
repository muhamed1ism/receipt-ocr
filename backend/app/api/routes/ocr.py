from fastapi import APIRouter, UploadFile

from app.ocr.image_loader import load_image
from app.ocr.ocr_service import run_ocr_with_fallback, validate_ocr_result

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post(
    "/scan",
)
async def scan(*, img_file: UploadFile):
    img = await load_image(img_file)
    results = run_ocr_with_fallback(image=img)
    return validate_ocr_result(results)
    # return img
