import streamlit as st
from pathlib import Path
from rag.run_qa_chain import run_custom_qa
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re

# ✅ 설정
st.set_page_config(page_title="전기차 정비 Q&A 어시스턴트", layout="wide")
st.title("🔧 전기차 정비 Q&A 어시스턴트")

# ✅ 헬퍼 함수


def extract_doc_title(path: str) -> str:
    """경로에서 문서 이름(.pdf 확장자 제거)만 추출"""
    return Path(path).stem


def clean_image_name(name: str) -> str:
    """_page0_img0.png 같은 뒷부분 제거"""
    return re.sub(r"_page\d+_img\d+\.png$", "", name)


# ✅ 입력창
query = st.text_input("질문을 입력하세요:", placeholder="예: 기능통합형 드라이브 액슬 탈거 방법 알려줘")

# ✅ 질문 처리
if query:
    with st.spinner("⏳ 답변 생성 중..."):
        result = run_custom_qa(query)

        # 좌우 2컬럼 레이아웃
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 🔧 정비사 답변")

            # [정비사 답변] 제거
            cleaned_answer = result["result"].removeprefix("[정비사 답변]").strip()
            st.success(cleaned_answer)

            st.markdown("### 📄 참고 문서")
            if not result["source_documents"]:
                st.warning("📄 관련 문서를 찾지 못했습니다.")
            else:
                for i, doc in enumerate(result["source_documents"], 1):
                    source_rel = doc.metadata.get("source", "")
                    source_name = Path(source_rel).stem  # 파일명 (확장자 제외)
                    file_path = Path.cwd() / source_rel  # 앱 실행 기준 상대 경로

                    if file_path.exists():
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"문서 {i}: {source_name}",
                                data=f.read(),
                                file_name=Path(source_rel).name,
                                mime="application/pdf"
                            )
                    else:
                        st.markdown(f"- 문서 {i}: `{source_name}` (⚠️ 파일 없음)")

            st.markdown(f"`{result['section']}`")
            st.markdown("### 📚 참고된 문서 청크")
            if not result["source_documents"]:
                st.info("관련 문서 청크가 없습니다.")
            else:
                for i, doc in enumerate(result["source_documents"], 1):
                    doc_title = doc.metadata.get("document", "제목 없음")
                    section = doc.metadata.get("section", "섹션 정보 없음")
                    full_text = doc.page_content.strip()

                    with st.expander(f"{i}. {doc_title} — 섹션: {section}"):
                        st.markdown(full_text)
                        
        with right_col:
            st.markdown("### 📷 관련 이미지")

            image_paths = result.get("image_paths", [])
            image_names = result.get("image_names", [])

            # 이미지 두 개씩 나눠서 두 열로 출력
            for i in range(0, len(image_paths), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(image_paths):
                        path = image_paths[i + j]
                        name = image_names[i + j]
                        display_name = name.rsplit("_page", 1)[0]  # _page0_img 제거

                        if path and Path(path).exists():  # ✅ 여기 수정
                            cols[j].image(
                                path,
                                caption=display_name,
                                use_container_width=True
                            )
