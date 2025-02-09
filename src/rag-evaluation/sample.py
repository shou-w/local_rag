import numpy as np
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
from sklearn.metrics.pairwise import cosine_similarity
from FlagEmbedding import FlagReranker
from langfuse.callback import CallbackHandler


langfuse_handler = CallbackHandler(
    secret_key=config.LANGFUSE_SECRET_KEY,
    public_key=config.LANGFUSE_PUBLIC_KEY,
    host="http://localhost:3000",
)


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
    return get_chain().invoke(
        {"input": question}, config={"callbacks": [langfuse_handler]}
    )


def get_cosine_similarity(question, chunk_list):
    query_embedding = get_embed_model().embed_query(question)
    chunk_embeddings = get_embed_model().embed_documents(chunk_list)
    query_embedding = np.array(query_embedding).reshape(1, -1)  # numpy配列に変換
    chunk_embeddings = np.array(chunk_embeddings)  # numpy配列に変換
    similarity_score_list = cosine_similarity(query_embedding, chunk_embeddings)
    return similarity_score_list


def get_reranker():
    reranker_model = "BAAI/bge-reranker-v2-m3"
    return FlagReranker(reranker_model, use_fp16=True)


def get_relevance_score(question, chunk_list):
    query_text_pairs = []
    for text in chunk_list:
        query_text_pairs.append([question, text])

    relevance_score_list = get_reranker().compute_score(
        query_text_pairs,
        normalize=True,
    )

    return relevance_score_list


def main():
    set_params()
    set_pdf_type()
    set_db_info()

    question = "この都市計画の概要を教えて下さい"
    result = execute_rag_chain(question)

    print(result["answer"])

    # chunk_list = [doc.page_content for doc in result["context"]]
    # similarity_score_list = get_cosine_similarity(question, chunk_list)
    # relevance_score_list = get_relevance_score(question, chunk_list)

    # for i in range(len(chunk_list)):
    #     print(f"\n\nチャンク {i+1}")
    #     if chunk_list and len(chunk_list[i]) >= 20:
    #         print(f"内容: {chunk_list[i][:20]}")
    #     elif chunk_list:
    #         print(f"内容: {chunk_list[i]}")
    #     else:
    #         print("内容: チャンクがありません")
    #     print(f"コサイン類似度: {similarity_score_list[0][i]}")
    #     print(f"関連度スコア: {relevance_score_list[i]}")


if __name__ == "__main__":
    main()
