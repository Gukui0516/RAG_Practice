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

# 출력
print("✅ 저장된 섹션 목록:")
for s in sorted(sections):
    print("-", s)
