# 베이스 이미지
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"

# 파일 복사
COPY . .

# pip 최신화 및 패키지 설치
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Streamlit 설정 (CORS off, 외부 접속 허용)
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
