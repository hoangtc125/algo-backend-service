import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import project_config
from app.core.filter import authentication, authorization
from app.core.exception import CustomHTTPException
from app.core.socket import socket_connection
from app.router.detect import router as detect_router
from app.router.account import router as account_router


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
    # if request.method != "OPTIONS":
    #     try:
    #         request_user = authentication(request)
    #     except CustomHTTPException as e:
    #         return JSONResponse(
    #             status_code=e.status_code,
    #             headers={
    #                 "access-control-allow-origin": "*",
    #                 "X-Process-Time": str(time.time() - start_time),
    #             },
    #             content=jsonable_encoder(
    #                 {"status_code": e.error_code, "msg": e.error_message}
    #             ),
    #         )
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.mount("/ws", socket_connection())

@app.post("/test_socket")
async def test_socket(event_name, data: str):
    return await socket_connection.send_data(
        channel=event_name,
        data=data
    )


app.include_router(detect_router)
app.include_router(account_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=project_config.ALGO_PORT)
