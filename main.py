import os
from typing import List
from fastapi import FastAPI, File, UploadFile

from src.config import load_config
from db.db_zoo import DatabaseRouter
from storage.storage_zoo import StorageRouter

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config=load_config(CURRENT_DIR)

db = DatabaseRouter.create(config["db"]["dbtype"])
storage = StorageRouter.create(config["storage"]["storagetype"])

app = FastAPI()

@app.post("/upload/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return 

@app.post("/download/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return 