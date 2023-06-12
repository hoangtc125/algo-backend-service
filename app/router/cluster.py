import asyncio
from typing import Dict, Optional
from fastapi import APIRouter

from app.core.model import HttpResponse, success_response
from app.core.api import ClusterApi
from app.service.loader import loader
from app.service.ssmc_fcm import SSMC_FCM
from app.model.cluster import Cluster
from app.util.model import get_dict
from app.worker.socket import SocketPayload, socket_worker
from app.util.time import get_current_timestamp

router = APIRouter()


@router.post(ClusterApi.VECTORIZE, response_model=HttpResponse)
async def vectorize(data: Dict, client_id: Optional[str] = None):
    for headerIndex, raw_data in data.items():
        item_data = [item.get("data") for item in raw_data["data"]]

        if client_id:
            socket_worker.push(
                SocketPayload(
                    data={
                        "time": get_current_timestamp(),
                        "content": f"Bắt đầu trích xuất đặc trưng {len(item_data)} dữ liệu {raw_data['type']} các bản ghi tại cột {headerIndex}",
                    },
                    channel="deployLog",
                    client_id=client_id,
                )
            )

        if raw_data["type"] == "categorical":
            vectors = await asyncio.create_task(
                loader.multilabel_binarizing(
                    raw_data=item_data, classes=raw_data["collDiffData"]
                )
            )
            for idx, vector in enumerate(vectors):
                data[headerIndex]["data"][idx]["data"] = vector.tolist()

        if raw_data["type"] == "numerical":
            vectors = await loader.numerical_vectorize(raw_data=item_data)
            for idx, vector in enumerate(vectors):
                data[headerIndex]["data"][idx]["data"] = vector

        if raw_data["type"] == "text":
            vectors = await asyncio.create_task(
                loader.feature_engineering(data=item_data, client_id=client_id)
            )
            for idx, vector in enumerate(vectors):
                data[headerIndex]["data"][idx]["data"] = vector.tolist()

        if client_id:
            socket_worker.push(
                SocketPayload(
                    data={
                        "time": get_current_timestamp(),
                        "content": f"Hoàn tất trích xuất đặc trưng {len(item_data)} dữ liệu {raw_data['type']} các bản ghi tại cột {headerIndex}",
                    },
                    channel="deployLog",
                    client_id=client_id,
                )
            )
    return success_response(data=data)


@router.post(ClusterApi.CLUSTERING, response_model=HttpResponse)
async def clustering(cluster: Cluster, client_id: Optional[str] = None):
    ssmc_fcm = SSMC_FCM(**get_dict(cluster))
    ssmc_fcm.clustering(client_id=client_id)
    ssmc_fcm.show_loss_function(client_id=client_id)
    return success_response(
        data={
            "pred_labels": ssmc_fcm.pred_labels,
            "membership": ssmc_fcm.membership,
        }
    )
