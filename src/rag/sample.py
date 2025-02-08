import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from decimal import Decimal, ROUND_HALF_UP
from chromadb.config import Settings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import config


pdf_import_format = ""
chunk_size = 0
chunk_overlap = 0


def main():
    print("main")
    set_params()
    set_pdf_type()
    set_db_info()
    question = "この都市計画の概要を教えて下さい"
    # question = "漫画ワンピースの作者は誰ですか？"
    execute_rag_chain(question)
    print("finish")


def set_params():
    print("set_params")
    global pdf_import_format, splitter_type, chunk_size, chunk_overlap
    pdf_import_format = "all"
    # pdf_import_format = "page"

    # splitter_type = "sentence"
    splitter_type = "character"

    chunk_size = 1000
    num = Decimal(chunk_size * 0.25)
    chunk_overlap = num.quantize(Decimal("0"), rounding=ROUND_HALF_UP)


def set_pdf_type():
    print("set_pdf_type")
    global pdf_type
    pdf_type = "kyoto"


def set_db_info():
    print("set_db_info")
    global persist_directory, collection_name
    persist_directory_name = f"db/chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{splitter_type}"
    persist_directory = os.path.abspath(persist_directory_name)
    collection_name = f"chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{splitter_type}"


def get_embed_model():
    print("get_embed_model")
    embed_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=config.OPENAI_API_KEY,
    )
    return embed_model


def get_vector_store():
    print("get_vector_store")
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=get_embed_model(),
        persist_directory=persist_directory,
        client_settings=Settings(allow_reset=True),
    )
    return vector_store


def get_llm():
    print("get_llm")
    model_name = "gpt-4o-mini"
    return ChatOpenAI(model=model_name, api_key=config.OPENAI_API_KEY)


def get_prompt():
    print("get_prompt")
    template = """
    あなたは、与えられたコンテキスト情報のみを使って質問に答えるAIアシスタントです。
    もし質問に答えるために十分な情報がコンテキストに含まれていない場合は、「コンテキスト情報から回答できません。」と答えてください。

    コンテキスト:
    {context}


    ユーザーの質問:
    {input}
    """

    return ChatPromptTemplate.from_template(template)


def get_chain():
    print("get_chain")
    llm = get_llm()
    vector_store = get_vector_store()
    prompt = get_prompt()
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(
        vector_store.as_retriever(
            search_kwargs={"k": 5},
        ),
        combine_docs_chain,
    )
    return rag_chain


def execute_rag_chain(question):
    print("execute_rag_chain")
    result = get_chain().invoke({"input": question})
    print("answer ==========================")
    print(result["answer"])


if __name__ == "__main__":
    main()
