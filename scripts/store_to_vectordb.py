import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import re
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from collections import defaultdict

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "chunks.json"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db" / "ev6"

embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# ✅ 텍스트 전처리 함수


def clean_text(text: str) -> str:
    text = text.replace('\u0001', ' ')
    text = re.sub(
        r'\d{2,4}\.\s?\d{1,2}\.\s?\d{1,2}\.(\s?(오전|오후)?\s?\d{1,2}:\d{2})?', '', text)
    text = re.sub(r'(https?://\S+|www\.\S+)', '', text)
    text = re.sub(r'\b[\w.-]+\.kia\.com\S*', '', text)
    text = re.sub(r'\b\d+/\d+\b', '', text)  # 슬라이드 번호 제거
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# ✅ 문서 단위 병합 후 LangChain Document 변환


def convert_to_documents(chunks: List[Dict]) -> List[Document]:
    doc_map = defaultdict(lambda: {"text": [], "image_paths": [], "meta": {}})

    for chunk in chunks:
        text = clean_text(chunk.get("text", ""))
        if not text:
            continue

        key = (chunk.get("section", "").strip().lower(),
               chunk.get("document", ""))
        doc_map[key]["text"].append(text)
        doc_map[key]["image_paths"].extend(chunk.get("image_paths", []))
        doc_map[key]["meta"] = {
            "section": chunk.get("section", "").strip().lower(),
            "document": chunk.get("document", ""),
            "source": chunk.get("source", ""),
            "category": chunk.get("category", "")
        }

    docs = []
    for (_, _), content in doc_map.items():
        full_text = "\n\n".join(content["text"])
        metadata = {
            **content["meta"],
            "image_paths": ", ".join(content["image_paths"]),
            "image_names": ", ".join([os.path.basename(p) for p in content["image_paths"]])
        }
        docs.append(Document(page_content=full_text, metadata=metadata))

    return docs

# ✅ JSON 파일 로드


def load_chunks(json_path: Path) -> List[Dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ✅ 벡터 DB 저장


def store_to_chroma(documents: List[Document], persist_path: Path):
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=str(persist_path)
    )
    vectordb.persist()
    print(f"✅ ChromaDB 저장 완료 → {persist_path}")


if __name__ == "__main__":
    print("📦 chunks.json 로딩 중...")
    chunks = load_chunks(CHUNKS_PATH)
    print(f"🔹 총 청크 수: {len(chunks)}")

    print("🧠 문서 단위로 임베딩 준비 중...")
    documents = convert_to_documents(chunks)
    print(f"✅ 변환된 문서 수: {len(documents)}")

    if documents:
        print(f"🔍 예시 문서 내용: {documents[0].page_content[:100]}...")
        print(f"🔍 예시 메타데이터: {documents[0].metadata}")

    print("💾 ChromaDB 저장 중...")
    store_to_chroma(documents, CHROMA_DIR)
