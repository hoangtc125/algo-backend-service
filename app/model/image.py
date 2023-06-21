from pydantic import BaseModel


class Image(BaseModel):
    uid: str
    name: str = ""
    status: str = "done"
    url: str
    type: str = "image/png"


class ImageResponse(Image):
    id: str


if __name__ == "__main__":
    pass
