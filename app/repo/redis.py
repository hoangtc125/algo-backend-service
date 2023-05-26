import redis

from app.core.config import project_config


class RedisConnection:
    def __init__(self):
        try:
            self.connection = redis.Redis(host=project_config.HOST, port=6379)
            response = self.connection.ping()
            if response:
                print(f"Connect to Redis")
        except redis.ConnectionError:
            print("Unable to connect to Redis")

    def get_connection(self):
        return self.connection

    def close_connection(self):
        self.connection.close()


redis_connection = RedisConnection()
