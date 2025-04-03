# Streamlit 앱 실행 파일
# app.py

import streamlit as st
from rag_chain import create_qa_chain

st.set_page_config(page_title="전기차 사용 매뉴얼 Q&A", layout="wide")
st.title("전기차 사용 매뉴얼 Q&A 어시스턴트")

# QA 체인 초기화
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = create_qa_chain()

query = st.text_input("❓ 궁금한 점을 입력하세요:", placeholder="예: 급속 충전 시 주의사항은 뭐야?")

if query:
    with st.spinner("답변을 생성 중입니다..."):
        result = st.session_state.qa_chain(query)
        st.write("### 💬 답변:")
        st.write(result['result'])

        # 선택적으로, 근거 문서 조각도 보여줄 수 있음
        with st.expander("📚 참고한 문서 조각 보기"):
            for i, doc in enumerate(result['source_documents']):
                st.markdown(
                    f"**{i+1}번 문서:**\n```\n{doc.page_content[:500]}\n```")

