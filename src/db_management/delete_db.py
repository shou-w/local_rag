import os
import shutil

pdf_import_format = ""
splitter_type = ""
chunk_size = 0


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


def delete_db():
    print("delete_db")
    persist_directory_name = f"db/chunking_evaluation-pdf_{pdf_type}_{chunk_size}_{pdf_import_format}_{splitter_type}"
    persist_directory = os.path.abspath(persist_directory_name)
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"Deleted directory: {persist_directory}")
    else:
        print(f"Directory not found: {persist_directory}")


def main():
    print("main")
    set_params()
    set_pdf_type()
    delete_db()
    print("finish")


if __name__ == "__main__":
    main()
