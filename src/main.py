from fastapi import FastAPI
import logging.config
from .config.logging import LOGGING

logging.config.dictConfig(LOGGING)

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/ping")
def ping():
    return {"ping": "PONG"}

@app.post("/scrape")
def scrape():
    
    
    return ...