import redis  # 导入redis 模块


class Mongo_Operate:
    def __init__(self):
        self.pool = redis.ConnectionPool(host='redis', port=6379, decode_responses=True)

