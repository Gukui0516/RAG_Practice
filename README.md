1. Python 가상환경 만들기 (venv)

```bash
python3 -m venv venv
```

2. 가상환경 활성화

```bash
source venv/bin/activat
```

3. 라이브러리 설치

```markdown
pip install -r requirements.txt
```

3.1 `langchain-community` 패키지 설치

```python
pip install -U langchain-community
```

3.2 tiktoken 패키지 설치

```python
pip install tiktoken
```

4. `.env` 파일에 API 키 추가

```markdown
OPENAI_API_KEY = 자신의 api 키
```

프로젝트 디렉토리
<img width="330" alt="스크린샷 2025-04-03 오전 9 50 51" src="https://github.com/user-attachments/assets/40749530-1e51-4745-b744-494f470b21bb" />

자신이 사용할 매뉴얼을 data 폴더에 pdf 저장하고 실행

## `ingest.py`: PDF → 임베딩 → Chroma 저장

실행
```python
python ingest.py
```

## `rag_chain.py GPT`+ Chroma를 연결하는 Retrieval QA 체인
## `app.py` – Streamlit 챗봇 인터페이스

실행

```python
streamlit run app.py
```

접속 화면
<img width="1710" alt="스크린샷 2025-04-03 오후 3 10 15" src="https://github.com/user-attachments/assets/a01bdeb6-4c97-44de-9de1-1dd3bc9af16c" />

