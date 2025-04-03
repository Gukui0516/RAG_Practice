# 문서 임베딩 및 Chroma DB 저장
# ingest.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma  
from dotenv import load_dotenv
import os

# 환경 변수 로드 (API 키 등)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def ingest_pdf():
    print("📄 PDF 로딩 중...")
    loader = PyPDFLoader("./data/sample_manual.pdf")
    documents = loader.load_and_split()  # 자동 페이지 분할

    print(f"📄 총 {len(documents)}개 문서로 분할 완료")

    print("🔍 OpenAI 임베딩 생성 중...")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    print("💾 Chroma DB에 저장 중...")
    vectordb = Chroma.from_documents(
        documents,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    vectordb.persist()
    print("✅ PDF 임베딩 및 DB 저장 완료!")


if __name__ == "__main__":
    ingest_pdf()
