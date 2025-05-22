import streamlit as st
from pathlib import Path
from rag.run_qa_chain import run_custom_qa
import os
import re

# ✅ 설정
st.set_page_config(page_title="EV6 정비 어시스턴트", layout="wide")
st.title("🔧 EV6 정비 문서 기반 Q&A")

# ✅ 헬퍼 함수


def extract_doc_title(path: str) -> str:
    """경로에서 문서 이름(.pdf 확장자 제거)만 추출"""
    return Path(path).stem


def clean_image_name(name: str) -> str:
    """_page0_img0.png 같은 뒷부분 제거"""
    return re.sub(r"_page\d+_img\d+\.png$", "", name)


# ✅ 입력창
query = st.text_input("🧠 질문을 입력하세요:", placeholder="예: 기능통합형 드라이브 액슬 탈거 방법 알려줘")

# ✅ 질문 처리
if query:
    with st.spinner("⏳ 답변 생성 중..."):
        result = run_custom_qa(query)

        # 좌우 2컬럼 레이아웃
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 🧠 정비사 답변")

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
                                label=f"📥 문서 {i}: {source_name}",
                                data=f.read(),
                                file_name=Path(source_rel).name,
                                mime="application/pdf"
                            )
                    else:
                        st.markdown(f"- 문서 {i}: `{source_name}` (⚠️ 파일 없음)")

            st.markdown(f"🔍 예측된 섹션: `{result['section']}`")

        with right_col:
            st.markdown("### 📷 관련 이미지")
            for path, name in zip(result.get("image_paths", []), result.get("image_names", [])):
                if path and Path(path).exists():
                    # 이미지 이름에서 "_page0_img1.png" 같은 접미어 제거
                    display_name = name.rsplit("_page", 1)[0]
                    st.image(
                        path,
                        caption=display_name,
                        use_container_width=True,
                        output_format="auto"
                    )
