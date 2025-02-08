import chromadb
import os

pdf_import_format = ""
splitter_type = ""
chunk_size = 0
persist_directory = ""
collection_name = ""
pdf_path = ""


def set_params():
    print("set_params")
    global pdf_import_format, splitter_type, chunk_size
    pdf_import_format = "all"
    # pdf_import_format = "page"

    splitter_type = "sentence"
    # splitter_type = "character"

    chunk_size = 1000


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


def reset_db():
    print("reset_db")
    chroma_client = chromadb.PersistentClient(
        path=persist_directory, settings=chromadb.Settings(allow_reset=True)
    )

    chroma_client.reset()


def main():
    print("main")
    set_params()
    set_pdf_type()
    set_db_info()
    reset_db()
    print("finish")


if __name__ == "__main__":
    main()
