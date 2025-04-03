# LangChain 기반 RAG 파이프라인 정의
# rag_chain.py

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# .env 로드
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


def create_qa_chain():
    # 벡터 DB 불러오기
    vectordb = Chroma(
        persist_directory="./chroma_db",
        embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key)
    )

    # GPT 모델 설정
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        model_name="gpt-4o"  #변경 가능
    )

    # QA 체인 구성
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    return qa_chain
