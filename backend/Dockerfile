FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 코드 복사 (app, interfaces, infrastructure, shared)
COPY app ./app
COPY interfaces ./interfaces
COPY infrastructure ./infrastructure
COPY shared ./shared
COPY alembic.ini .
COPY alembic ./alembic
COPY pyproject.toml .

# Python 경로 설정
ENV PYTHONPATH="/app:$PYTHONPATH"

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]