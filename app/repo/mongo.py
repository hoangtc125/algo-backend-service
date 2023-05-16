from typing import TypeVar, Dict
from pymongo import MongoClient
from uuid import uuid4

from app.util.model import get_dict


T = TypeVar("T")

class MongoDBConnection:

    repositories = {}
    connection = None

    def __init__(self, url):
        print(f"Connect to MongoDB at {url}")
        self.client = MongoClient(url)

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
    def __init__(self, connection, collection_name):
        self.collection = connection[collection_name]
        self.model = collection_name

    async def get_one(self, field: str, value: str):
        return await self.collection.find_one({field: value})

    async def get_one_by_id(self, value: str):
        return await self.get_one("_id", value)

    async def get_all(self, page_size = 20, page_number = None, query = {}):
        if not page_number:
            cursor = self.collection.find(query)
        else:
            skip = page_size * (page_number - 1)
            cursor = self.collection.find().skip(skip).limit(page_size)
        return [document async for document in cursor]

    async def insert(self, obj: T, custom_id=None):
        if obj.__class__ != self.model:
            raise TypeError(
                f"{obj.__class__} can not be inserted into {self.model.__class__}"
            )
        _id = custom_id if custom_id else uuid4()
        result = await self.collection.insert_one({"_id": _id, **get_dict(obj)})
        return str(result.inserted_id)

    async def update(self, query: Dict, update_data: Dict):
        return await self.collection.update_one(query, {"$set": update_data})

    async def update_one(self, id, update_data: Dict):
        return await self.collection.update_one({"_id": id}, {"$set": update_data})

    async def delete(self, query: Dict):
        return await self.collection.delete_one(query)


def get_repo(model: T, url: str, db: str, new_connection: bool = False) -> BaseRepository:
    connection = MongoDBConnection.mongodb(url, db)
    collection_name = model.__name__
    if new_connection:
        return BaseRepository(connection, collection_name)
    if MongoDBConnection.repositories.get(collection_name, None) is None:
        MongoDBConnection.repositories[collection_name] = BaseRepository(connection, collection_name)
    return MongoDBConnection.repositories[collection_name]
