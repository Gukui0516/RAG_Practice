import os
from pathlib import Path


def count_pdfs(directory: str) -> int:
    pdf_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_count += 1
    return pdf_count


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent / "data/pdfs"  # 예시 경로
    total_pdfs = count_pdfs(str(base_dir))
    print(f"총 PDF 문서 수: {total_pdfs}")
