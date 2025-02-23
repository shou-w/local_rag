import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from fastapi import FastAPI
import rag.sample as rag

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/rag/{question}")
def read_item(question: str):
    return rag.main(question)
