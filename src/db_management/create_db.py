import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pypdf import PdfReader
from chromadb.config import Settings
from decimal import Decimal, ROUND_HALF_UP
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
import config

pdf_import_format = ""
splitter_type = ""
chunk_size = 0
chunk_overlap = 0
persist_directory = ""
collection_name = ""
pdf_path = ""


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


def set_pdf():
    print("set_pdf")
    global pdf_name, pdf_type, pdf_path
    pdf_type = "kyoto"
    pdf_name = "京都市基本計画.pdf"
    pdf_path = os.path.abspath(f"data/{pdf_name}")


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


def get_documents():
    print("get_documents")
    reader = PdfReader(pdf_path)
    documents = []

    if pdf_import_format == "page":
        print("page")
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():  # 空のページをスキップ
                documents.append(Document(page_content=text))
    else:
        print("all")
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += page.extract_text()

        documents = [Document(page_content=text)]

    return documents


def get_splitter():
    print("get_splitter")
    return CharacterTextSplitter(
        separator="。",  # セパレータ
        chunk_size=chunk_size,  # チャンクの文字数
        chunk_overlap=chunk_overlap,  # チャンクオーバーラップの文字数
        is_separator_regex=False,
    )


def save_documents():
    print("save_documents")
    docs = get_splitter().split_documents(get_documents())
    get_vector_store().add_documents(documents=docs)
    print("ベクトルDBへのデータ保存が完了しました。")


def main():
    print("main")
    set_params()
    set_pdf()
    set_db_info()
    save_documents()
    print("finish")


if __name__ == "__main__":
    main()
