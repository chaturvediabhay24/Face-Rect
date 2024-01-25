import os
from pymongo import MongoClient
from loguru import logger
import numpy as np

from .db_base import DBBase

class MongoConnectionManager:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = MongoClient(os.getenv("DB_CONNECTION_URL", "mongodb://localhost:27017"))
        return cls._client

    @classmethod
    def close_client(cls):
        if cls._client is not None:
            cls._client.close()
            cls._client = None

class MongoDB(DBBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.client = MongoConnectionManager.get_client()
        self.db = self.client[self.db_name]
        self.embedding_table = self.db[self.embedding_table_name]
        self.config_table = self.db[self.config_table_name]
        self.events_table = self.db[self.events_table_name]

    def nested_array_to_list(self, arr):
        if isinstance(arr, np.ndarray):
            return arr.tolist()
        elif isinstance(arr, list):
            return [self.nested_array_to_list(item) for item in arr]
        else:
            return arr
    
    def format_data(self, embedding):
        response = []
        for emb in embedding:
            d={}
            for key, values in emb.items():
                if isinstance(values, type(np.array([]))):
                    d[key]=self.nested_array_to_list(values)
                elif type(values) in [np.float16, np.float32, np.float64, np.float128]:
                    d[key]=float(values)
                else:
                    d[key]=values
            response.append(d)
        return response


    def add_embeddings(self, embedding):
        try:
            embedding = self.format_data(embedding)
            logger.info(f"embedding {embedding}")
            x = self.embedding_table.insert_many(embedding)
            logger.info(f"Insertion Complete : {x}")
        except Exception as e:
            logger.error(f"Database insertion failed: {e}", exc_info=True)

    def get_embeddings(self, event_id):
        try:
            x = self.embedding_table.find({"event_id": event_id})
            logger.info(f"Fetching Complete : {x}")
            return list(x)
        except Exception as e:
            logger.error(f"Database fetching failed: {e}", exc_info=True)
            return []

    def is_event_exist(self, event_id):
        events = self.events_table.find_one({"event_id": event_id})
        if events:
            return True
        return False
    
    def add_event(self, event):
        try:
            x = self.events_table.insert_one(event)
            logger.info(f"Insertion Complete : {x.inserted_id}")
        except Exception as e:
            logger.error(f"Database insertion failed: {e}", exc_info=True)