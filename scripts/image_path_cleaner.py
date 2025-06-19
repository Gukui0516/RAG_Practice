#청크파일에서 존재하지 않는 이미지 경로를 제거
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json

# 파일 경로
input_path = "data/chunks.json"
output_path = "data/chunks_cleaned.json"

# JSON 로드
with open(input_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 이미지 경로 정리
for chunk in chunks:
    image_paths = chunk.get("image_paths", [])
    # 실제로 존재하는 경로만 유지
    chunk["image_paths"] = [path for path in image_paths if os.path.exists(path)]

# 결과 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"✅ 정리 완료: {output_path}에 저장됨.")