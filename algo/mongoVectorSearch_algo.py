from time import time
import numpy as np
import importlib
from loguru import logger

from algo.algo_base import AlgoBase

class MongovectorsearchAlgo(AlgoBase):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.index_folder_name = "mongoVectorSearch_indexes"
        self.embeding_dimensions = int(config["algo"]["embedding_dimensions"])
        self.index_name = config["algo"]["index_name"]
    
    def download(self, config, files):
        config["index_name"] = self.index_name
        uploaded_files = self.storage.save_image_to_storage({"event_id": "search"}, files)

        results = []
        for file in uploaded_files:
            embeddings = self.model.get_embeddings(file)
            for embedding in embeddings:
                result = self.db.search_vector_embeddings(queryVector = embedding, config=config)
                results.extend(result)

        return results


    def upload(self, config, files):
        logger.info("Saving files locally.")
        uploaded_files = self.storage.save_image_to_storage(config, files)

        logger.info("Getting embeddings.")
        final_embeddings = []
        for file in uploaded_files:
            embeddings = self.model.get_embeddings(file)
            for embedding in embeddings:
                embedding = dict(embedding)
                embedding["event_id"] = config["event_id"]
                embedding["file_name"] = file
                embedding["timestamp"] = int(time()*(10**7))
                final_embeddings.append(embedding)

        logger.info("Saving embeddings to DB.")
        self.db.add_embeddings(final_embeddings)
        logger.info("UPLOAD COMPLETE!!!")
                