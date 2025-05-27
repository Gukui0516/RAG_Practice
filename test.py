from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_db" / "ev6"

# Azure 임베딩 (필요 없지만 Chroma 로딩을 위해 필요)
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Chroma 로드
vectordb = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embedding_model
)

# 메타데이터에서 섹션만 추출
collection = vectordb._collection.get(include=["metadatas"])
sections = set()

for metadata in collection["metadatas"]:
    section = metadata.get("section", "").strip()
    if section:
        sections.add(section)

# 저장된 문서 중 하나를 예시로 출력
docs = vectordb.similarity_search("test", k=1)
if docs:
    doc = docs[0]
    print("✅ 예시 문서 내용:")
    print(doc.page_content)
    print("\n✅ 메타데이터:")
    for key, value in doc.metadata.items():
        print(f"{key}: {value}")
else:
    print("❌ 관련 문서를 찾을 수 없습니다.")
