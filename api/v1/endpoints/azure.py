from fastapi import APIRouter


router = APIRouter()


@router.get("/azure/ocr")
def init():
    return {"tag": "azure ocr"}
