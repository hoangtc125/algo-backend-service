import time
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import project_config
from app.core.filter import authentication, authorization
from app.core.exception import CustomHTTPException
from app.core.socket import socket_connection
from app.core.log import logger
from app.router.detect import router as detect_router
from app.router.account import router as account_router
from app.worker.socket import socket_worker


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(CustomHTTPException)
async def uvicorn_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.error_code, "msg": exc.error_message},
    )


@app.middleware("http")
async def add_request_middleware(request: Request, call_next):
    start_time = time.time()
    if request.method == "OPTIONS":
        return Response()
    try:
        request_user = authentication(request)
        logger.log(request, request_user, tag=logger.tag.START)
        authorization(
            path=request.url.path,
            request_role=request_user.role,
            request_host=request.client.host,
            request=request,
        )
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time() - start_time)
    except CustomHTTPException as e:
        response = JSONResponse(
            status_code=e.status_code,
            headers={
                "access-control-allow-origin": "*",
                "X-Process-Time": str(time.time() - start_time),
            },
            content=jsonable_encoder(
                {"status_code": e.error_code, "msg": e.error_message}
            ),
        )
    except Exception as e:
        response = JSONResponse(
            status_code=500,
            headers={
                "access-control-allow-origin": "*",
                "X-Process-Time": str(time.time() - start_time),
            },
            content=jsonable_encoder({"status_code": 500, "msg": str(e)}),
        )
    finally:
        logger.log(request.url.path, response, tag=logger.tag.END)
        return response


app.mount("/ws", socket_connection())


@app.post("/test_socket")
def test_socket(event, data: str):
    socket_worker.push(event=event, data=data)


app.include_router(detect_router)
app.include_router(account_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=project_config.ALGO_PORT)
