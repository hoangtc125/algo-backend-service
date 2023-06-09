import time
import traceback
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import project_config
from app.core.filter import authentication, authorization
from app.core.exception import CustomHTTPException
from app.core.socket import socket_connection
from app.core.log import logger
from app.core.constant import Queue
from app.core.model import SocketPayload
from app.core.terminal import server_info, services_info
from app.model.notification import SocketNotification

# from app.router.detect import router as detect_router
from app.router.account import router as account_router
from app.router.image import router as image_router

from app.router.cluster import router as cluster_router
from app.router.club import router as club_router
from app.router.recruit import router as recruit_router
from app.util.model import get_dict
from app.worker.socket import socket_worker
from app.queue.rabbitmq import rabbitmq


app = FastAPI(docs_url=None, redoc_url=None)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
).instrument(app)


@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)
    services_info()


@app.on_event("shutdown")
async def _shutdown_event():
    try:
        server_info()
    except:
        pass


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


from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.middleware("http")
async def add_request_middleware(request: Request, call_next):
    start_time = time.time()
    url_path = request.url.path
    log_excepts = ["/metrics"]
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response
    try:
        request_user = authentication(request)
        if url_path not in log_excepts:
            logger.log(request, request_user, tag=logger.tag.START)
        authorization(
            path=url_path,
            request_role=request_user.role,
            request_host=request.client.host,
            request=request,
        )
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time() - start_time)
        if url_path not in log_excepts:
            logger.log(url_path, response, tag=logger.tag.END)
        return response
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
        if url_path not in log_excepts:
            logger.log(url_path, response, tag=logger.tag.END)
        return response
    except Exception as e:
        traceback.print_exc()
        response = JSONResponse(
            status_code=500,
            headers={
                "access-control-allow-origin": "*",
                "X-Process-Time": str(time.time() - start_time),
            },
            content=jsonable_encoder({"status_code": 500, "msg": str(e)}),
        )
        if url_path not in log_excepts:
            logger.log(url_path, response, tag=logger.tag.END)
        return response


app.mount("/ws", socket_connection())


@app.get("/")
def docs():
    return RedirectResponse(url="/docs")


@app.post("/test/socket")
def test_socket(socket_payload: SocketNotification):
    socket_worker.push(socket_payload=SocketPayload(**get_dict(socket_payload)))


@app.post("/test/rabbitmq")
def test_rabbitmq(socket_payload: SocketNotification):
    rabbitmq.send(
        queue_name=Queue.SOCKET, message=SocketPayload(**get_dict(socket_payload))
    )


# app.include_router(detect_router)
app.include_router(account_router)
app.include_router(image_router)
app.include_router(cluster_router)
app.include_router(club_router)
app.include_router(recruit_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=project_config.ALGO_PORT,
        # ssl_keyfile=project_config.SSL_KEY,
        # ssl_certfile=project_config.SSL_CERT,
    )
