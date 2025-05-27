# PDF 문서에서 텍스트와 이미지를 추출하여 구조화된 JSON 파일로 저장
# 1.	📄 PDF 문서를 탐색하여 모든 페이지의 텍스트와 이미지를 추출하고, 경로 정보를 바탕으로 섹션/문서명을 구분합니다.
# 2.	🧹 텍스트는 날짜·링크·제어문자 등을 제거해 정제하고, 이미지 파일은 페이지별로 PNG 형식으로 저장합니다.
# 3.	🗂 정제된 텍스트, 이미지 경로, 원본 경로, 섹션명, 문서명을 포함한 JSON 데이터를 생성해 하나의 파일로 저장합니다.

import os
import fitz  # PyMuPDF
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict


def extract_from_pdf(pdf_path: str, output_image_dir: str) -> List[Dict]:
    Path(output_image_dir).mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    # ✅ 상대 경로 및 섹션, 문서 이름 추출 (NFC 정규화)
    relative_path = os.path.relpath(pdf_path)
    parts = [unicodedata.normalize("NFC", p)
             for p in Path(relative_path).parts]

    try:
        ev6_index = parts.index("ev6 정비 지침서")
        section = parts[ev6_index + 1]
        document = parts[ev6_index + 2] if len(parts) > ev6_index + 2 else ""
    except (ValueError, IndexError):
        section = "기타"
        document = ""

    full_text = ""
    image_paths = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        raw_text = page.get_text("text")

        # ✅ 제어 문자 제거 및 정리
        raw_text = raw_text.replace('\u0001', ' ')
        raw_text = re.sub(
            r'\d{2,4}\.\s?\d{1,2}\.\s?\d{1,2}\.(\s?(오전|오후)\s?\d{1,2}:\d{2})?', '', raw_text)
        raw_text = re.sub(r'(https?://\S+|www\.\S+)', '', raw_text)
        raw_text = re.sub(r'\b[\w.-]+\.kia\.com\S*', '', raw_text)
        raw_text = re.sub(r'\b\d+/\d+\b', '', raw_text)
        raw_text = re.sub(r'\s{2,}', ' ', raw_text).strip()

        if raw_text:
            full_text += raw_text + "\n\n"

        # ✅ 이미지 추출
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            base_name = Path(pdf_path).stem
            image_filename = f"{base_name}_page{page_num}_img{img_index}.png"
            image_path = os.path.join(output_image_dir, image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)

    if full_text:
        return [{
            "text": full_text.strip(),
            "image_paths": image_paths,
            "source": relative_path,
            "section": section,
            "document": document
        }]
    else:
        return []


def get_all_pdf_paths(base_dir: str) -> List[str]:
    pdf_paths = []
    print(f"📂 루트 디렉토리: {base_dir}\n")

    for root, dirs, files in os.walk(base_dir):
        print(f"🔎 현재 디렉토리: {root}")
        print(f"   ├─ 하위 폴더 수: {len(dirs)}, 파일 수: {len(files)}")

        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                print(f"     📄 PDF 발견: {full_path}")
                pdf_paths.append(full_path)

    print(f"\n📦 총 발견된 PDF 수: {len(pdf_paths)}\n")
    return pdf_paths


def extract_all_pdfs(pdf_dir: str, image_dir: str, output_json: str):
    all_chunks = []
    pdf_paths = get_all_pdf_paths(pdf_dir)
    print(f"🔍 총 PDF 수: {len(pdf_paths)}\n")

    for pdf_path in pdf_paths:
        print(f"📄 추출 중: {pdf_path}")
        chunks = extract_from_pdf(pdf_path, image_dir)
        all_chunks.extend(chunks)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 전체 추출 완료! 저장 위치 → {output_json}")
    print(f"📦 총 청크 수: {len(all_chunks)}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    extract_all_pdfs(
        pdf_dir=str(BASE_DIR / "data/pdfs"),
        image_dir=str(BASE_DIR / "data/images"),
        output_json=str(BASE_DIR / "data/chunks.json")
    )