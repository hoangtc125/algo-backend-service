from typing import Dict

from app.core.config import project_config
from app.repo.mongo import get_repo
from app.model.image import Image


class ImageService:
    def __init__(self):
        self.image_repo = get_repo(
            Image,
            url=project_config.MONGO_URL,
            db=project_config.MONGO_DB,
            new_connection=False,
        )

    async def get_image(self, query: Dict):
        res = await self.image_repo.get_one(query)
        if not res:
            return None
        id, image = res
        return image

    async def get_all(self, **kargs):
        images = await self.image_repo.get_all(**kargs)
        res = []
        for doc_id, uv in images.items():
            res.append(uv)
        return res

    async def save(self, image: Image):
        try:
            doc_id = await self.image_repo.insert(image, image.uid)
            return doc_id
        except:
            pass

    async def update(self, image: Image):
        try:
            doc_id = await self.image_repo.update_by_id(id=image.uid, obj=image)
            return doc_id
        except:
            pass
