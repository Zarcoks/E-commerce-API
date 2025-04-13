from rq import Queue
from .redis_config import redis_client
    

queue = Queue(connection=redis_client)