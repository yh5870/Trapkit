FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY app ./app
COPY pyproject.toml .
COPY alembic.ini .
COPY alembic ./alembic

# 비밀번호 파일 생성 (Alembic용)
RUN mkdir -p /app/alembic/versions && touch /app/.env

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]