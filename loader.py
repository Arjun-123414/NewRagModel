#pip install "unstructured[all-docs]"
from langchain_community.document_loaders import PyPDFLoader, UnstructuredExcelLoader

def load_document(file_path):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        return loader.load()   # page-wise docs

    elif file_path.endswith(".xlsx"):
        loader = UnstructuredExcelLoader(file_path)
        return loader.load()

    else:
        raise ValueError("Unsupported file type")
