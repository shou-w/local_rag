import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from fastapi import FastAPI
import rag.sample as rag
import api.question as question

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/rag/")
async def chat(req: question.Question):
    question = req.question
    return rag.main(question)
