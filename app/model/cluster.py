from typing import List
from pydantic import BaseModel


class Cluster(BaseModel):
    identity: List
    supervised_set: List
    fields_len: List
    fields_weight: List
    dataset: List


class ClusterResponse(Cluster):
    id: str


if __name__ == "__main__":
    pass
