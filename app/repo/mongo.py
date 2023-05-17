import traceback
from  motor.motor_asyncio import AsyncIOMotorClient
from typing import TypeVar, Dict
from uuid import uuid4

from app.util.model import get_dict, get_response_model


T = TypeVar("T")


class MongoDBConnection:

    repositories = {}
    connection = None

    def __init__(self, url):
        print(f"Connect to MongoDB")
        self.client = AsyncIOMotorClient(url)

    def get_connection(self, database):
        return self.client[database]

    def close_connection(self):
        self.client.close()

    @classmethod
    def mongodb(self, url, db):
        if MongoDBConnection.connection is None:
            MongoDBConnection.connection = MongoDBConnection(url).get_connection(db)
        return MongoDBConnection.connection


class BaseRepository:
    def __init__(self, connection, model):
        self.collection = connection[model.__name__.lower()]
        self.model = model

    async def get_one(self, query):
        try:
            res = await self.collection.find_one(query)
            if not res:
                return None
        except:
            traceback.print_exc()
            return None
        return (str(res["_id"]), self.model(**res["_source"]))

    async def get_one_by_id(self, value: str):
        try:
            res = await self.collection.find_one({"_id": value})
            if not res:
                return None
        except:
            traceback.print_exc()
            return None
        return (str(res["_id"]), self.model(**res["_source"]))

    async def get_all(self, page_size = 20, page_number = None, query = {}):
        if not page_number:
            cursor = self.collection.find(query)
        else:
            skip = page_size * (page_number - 1)
            cursor = self.collection.find(query).skip(skip).limit(page_size)
        res = {}
        async for document in cursor:
            res[document["_id"]] = get_response_model(document, self.model)
        return res

    async def insert(self, obj: T, custom_id=None):
        if obj.__class__ != self.model:
            raise TypeError(
                f"{obj.__class__} can not be inserted into {self.model.__class__}"
            )
        _id = custom_id if custom_id else str(uuid4())
        result = await self.collection.insert_one({"_id": _id, "_source": get_dict(obj)})
        return str(result.inserted_id)

    async def update(self, query: Dict, obj: Dict):
        await self.collection.update_one(query, {"$set": obj})
        return id

    async def update_by_id(self, id, obj: Dict):
        await self.collection.update_one({"_id": id}, {"$set": obj})
        return id

    async def delete(self, query: Dict):
        return await self.collection.delete_one(query)


def get_repo(model: T, url: str, db: str, new_connection: bool = False) -> BaseRepository:
    connection = MongoDBConnection.mongodb(url, db)
    collection_name = model.__name__.lower()
    if new_connection:
        return BaseRepository(connection, model)
    if MongoDBConnection.repositories.get(collection_name, None) is None:
        MongoDBConnection.repositories[collection_name] = BaseRepository(connection, model)
    return MongoDBConnection.repositories[collection_name]
