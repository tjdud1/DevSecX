# Python 3.12-slim 베이스 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일 복사 및 의존성 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 모든 소스코드 복사
COPY . /app

# 포트 노출 (여기서는 3389 포트를 사용)
EXPOSE 3389

# 컨테이너 실행 시, app.py 파일 실행 (Streamlit 앱 실행)
CMD ["streamlit", "run", "app.py", "--server.port", "3389", "--server.enableCORS", "false"]
