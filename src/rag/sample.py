from pypdf import PdfReader
import chromadb
from chromadb.config import Settings
from google.colab import userdata
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import numpy as np
from FlagEmbedding import FlagReranker


pdf_import_format = "all"
# pdf_import_format = "page"

# spritter_type = "sentence"
spritter_type = "character"

from decimal import Decimal, ROUND_HALF_UP

# chunk_size = 500
chunk_size = 1000
# chunk_size = 1500
# chunk_size = 2000
num = Decimal(chunk_size * 0.25)
chunk_overlap = num.quantize(Decimal("0"), rounding=ROUND_HALF_UP)

pdf_type = "digital"

# pdf_type = "giga"

persist_directory = f"/content/drive/MyDrive/Colab Notebooks/CYLLENGE/Chroma/chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{spritter_type}"
collection_name = f"chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{spritter_type}"

from langchain_openai import OpenAIEmbeddings

embed_model = OpenAIEmbeddings(
    model="text-embedding-3-large", api_key=userdata.get("MY_OPENAI_KEY")
)

from langchain_chroma import Chroma

vector_store = Chroma(
    client_settings=Settings(allow_reset=True),
    collection_name=collection_name,
    embedding_function=embed_model,
    persist_directory=persist_directory,
)

from langchain_openai import ChatOpenAI

model_name = "gpt-4o-mini"
llm = ChatOpenAI(model=model_name, api_key=userdata.get("MY_OPENAI_KEY"))

from langchain.prompts import ChatPromptTemplate

template = """
あなたは、与えられたコンテキスト情報のみを使って質問に答えるAIアシスタントです。
もし質問に答えるために十分な情報がコンテキストに含まれていない場合は、「コンテキスト情報から回答できません。」と答えてください。

コンテキスト:
{context}


ユーザーの質問:
{input}
"""

prompt = ChatPromptTemplate.from_template(template)

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(
    vector_store.as_retriever(
        search_kwargs={"k": 5},
    ),
    combine_docs_chain,
)

question = "この都市計画の概要を教えて下さい"
result = rag_chain.invoke({"input": question})
print(result["answer"])
