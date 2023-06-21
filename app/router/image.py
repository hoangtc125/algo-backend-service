from fastapi import APIRouter

from app.core.api import ImageApi
from app.core.model import success_response
from app.service.image import ImageService


router = APIRouter()


@router.get(ImageApi.GET)
async def get_image(id: str):
    result = await ImageService().get_image({"_id": id})
    return success_response(result)
