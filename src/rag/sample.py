import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import config

from decimal import Decimal, ROUND_HALF_UP
from chromadb.config import Settings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate


pdf_import_format = ""
chunk_size = 0
chunk_overlap = 0

query_list = [
    "京都市基本計画の計画期間は、何年から何年までですか？",
    "京都市が掲げる都市理念は何ですか？",
    "京都市が重点戦略として掲げる「世界の文化首都・京都戦略」を推進する上で、市民・団体、企業・事業者、行政はそれぞれどのような役割を担うことが期待されていますか？",
    "京都市が持続可能な行財政の確立に向けて取り組むべき課題として、財政構造の抜本的な改革、歳出改革、行財政運営の効率化、の他にどのようなことを重要視していますか？また、その理由について説明してください。",
    "京都市内にある国宝の数は何件ですか？",
    "京都市の人口を男女別に見た時の割合は？",
    "京都で有名な観光スポットの周辺にある美味しいラーメン屋を３つ教えてください。",
    "今日、京都市内は何℃ですか？",
]


def set_params():
    global pdf_import_format, splitter_type, chunk_size, chunk_overlap
    pdf_import_format = "all"
    # pdf_import_format = "page"

    # splitter_type = "sentence"
    splitter_type = "character"

    chunk_size = 1000
    num = Decimal(chunk_size * 0.25)
    chunk_overlap = num.quantize(Decimal("0"), rounding=ROUND_HALF_UP)


def set_pdf_type():
    global pdf_type
    pdf_type = "kyoto"


def set_db_info():
    global persist_directory, collection_name
    persist_directory_name = f"db/chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{splitter_type}"
    persist_directory = os.path.abspath(persist_directory_name)
    collection_name = f"chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{splitter_type}"


def get_embed_model():
    embed_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=config.OPENAI_API_KEY,
    )
    return embed_model


def get_vector_store():
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=get_embed_model(),
        persist_directory=persist_directory,
        client_settings=Settings(allow_reset=True),
    )
    return vector_store


def get_llm():
    model_name = "gpt-4o-mini"
    return ChatOpenAI(model=model_name, api_key=config.OPENAI_API_KEY)


def get_prompt():
    template = """
    与えられたコンテキスト情報を使って、ユーザーの質問に答えてください。

    コンテキスト:
    {context}


    ユーザーの質問:
    {input}
    """

    return ChatPromptTemplate.from_template(template)


def get_chain():
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
    result = get_chain().invoke({"input": question})
    # print("answer ==========================")
    # print(result["answer"])
    return result["answer"]


def main(question=None):
    set_params()
    set_pdf_type()
    set_db_info()

    if question is None:
        question = "この都市計画の概要を教えて下さい"

    return execute_rag_chain(question)

    # for query in query_list:
    #     print("\n\nquery ==========================")
    #     print(query)
    #     execute_rag_chain(query)


if __name__ == "__main__":
    main()
