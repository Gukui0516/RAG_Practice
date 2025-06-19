import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import textwrap
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain

load_dotenv()

# ✅ 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_db" / "ev6"

# ✅ 임베딩 모델
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# ✅ LLM 모델
local_llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.2,
    model_name="gpt-4o"
)

# ✅ Chroma 벡터 DB
vectordb = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embedding_model
)

# ✅ 응답 생성 프롬프트 템플릿
qa_prompt = PromptTemplate.from_template(textwrap.dedent("""
    당신은 전기차 정비 문서에 기반하여 질문에 답하는 전문 정비사입니다.

    - 문서에서 유사하거나 관련 있는 내용을 참고하여 단계별로 설명하세요.
    - 직접적인 문장이 없더라도, 문맥상 유추 가능한 경우는 '문서에 따르면...'의 형식으로 정리해 주세요.
    - 단, 완전히 문서에 없을 경우에는 '문서에 없는 내용이라 답변 드릴 수 없습니다.'라고 말하세요.

    [문서 내용]
    {context}

    [질문]
    {question}

    [정비사 답변]
"""))

# ✅ 섹션 분류 프롬프트
section_prompt = PromptTemplate.from_template(textwrap.dedent("""
다음 사용자의 질문이 어느 전기차 정비 시스템 섹션에 가장 관련 있는지 아래 선택지 중 하나만 골라주세요.

선택지:
드라이브 샤프트 및 액슬
모터 및 감속기 시스템
바디 (내장 및 외장)
바디 전장
배터리 제어 시스템
브레이크 시스템
서스펜션 시스템
스티어링 시스템
에어백 시스템
일반사항
전기차 냉각 시스템
첨단 운전자 보조 시스템(ADAS)
히터 및 에어컨 장치

질문: {question}

가장 관련 있는 섹션:
"""))

# ✅ 문서 추론 프롬프트
document_prompt = PromptTemplate.from_template(textwrap.dedent("""
다음은 "{section}" 섹션의 문서 목록입니다:

{document_list}

사용자의 질문: {question}

위 문서 중에서 가장 관련 있는 문서명을 정확히 골라주세요. 반드시 목록에 있는 문서명과 일치시켜 출력하세요.

선택한 문서명:
"""))

section_chain = LLMChain(llm=local_llm, prompt=section_prompt)
document_chain = LLMChain(llm=local_llm, prompt=document_prompt)

# ✅ 커스텀 QA 실행 함수
def run_custom_qa(query: str):
    # 1. 섹션 추론
    section = section_chain.run({"question": query}).strip()

    # 2. 섹션 내 문서 후보 수집
    all_metadata = vectordb.get()["metadatas"]
    section_docs = {meta["document"]
                    for meta in all_metadata if meta.get("section") == section}
    document_list_str = "\n".join(sorted(section_docs))

    # 3. 문서 추론
    document = document_chain.run({
        "question": query,
        "section": section,
        "document_list": document_list_str
    }).strip()

    # 4. 관련 문서 검색 (문서 필터만 사용)
    retriever = vectordb.as_retriever(
        search_kwargs={"k": 10, "filter": {"document": document}}
    )
    query_with_doc = f"{query} 관련 문서: {document}"
    docs = retriever.invoke(query_with_doc)

    # 5. 문맥 생성 및 답변 생성
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = (
        {"context": lambda _: context, "question": lambda _: query}
        | qa_prompt
        | local_llm
        | StrOutputParser()
    )
    answer = chain.invoke({})

    # 6. 이미지 정보 정리
    image_paths = []
    image_names = []
    for doc in docs:
        meta = doc.metadata
        if "image_paths" in meta:
            image_paths.extend([p.strip()
                               for p in meta["image_paths"].split(",")])
        if "image_names" in meta:
            image_names.extend([n.strip()
                               for n in meta["image_names"].split(",")])

    return {
        "result": answer,
        "section": section,
        "document": document,
        "source_documents": docs,
        "image_paths": image_paths,
        "image_names": image_names
    }