import json
import os
from pathlib import Path

# 🔧 절대 경로 기준점 (이 경로부터 상대 경로로 바꿔줌)
PROJECT_ROOT = Path("/Users/gukui/Develop/Rag/data/").resolve()

# 🔧 대상 JSON 파일 경로
JSON_PATH = PROJECT_ROOT / "chunks.json"

# 🔄 처리 시작
with open(JSON_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

for chunk in chunks:
    if "image_paths" in chunk:
        new_paths = []
        for path in chunk["image_paths"]:
            new_paths.append("data/" + path)
        chunk["image_paths"] = new_paths

# 💾 덮어쓰기 or 새로운 파일로 저장
with open(PROJECT_ROOT / "chunks_rewritten.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print("✅ image_paths 경로를 상대 경로로 변환 완료 → chunks_rewritten.json 저장됨")
