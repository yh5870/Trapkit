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

# 포트 노출 (로컬/docker-compose 기본값)
EXPOSE 8000

# 실행 명령
# Render 등 PaaS는 포트를 $PORT 환경변수로 주입하며, 그 포트로 리스닝하지
# 않으면 헬스체크에 실패해 배포가 뜨지 않는다. 로컬에서는 $PORT가 없으므로
# 8000으로 폴백한다. 셸 확장이 필요하므로 exec 형식이 아닌 shell 형식 사용.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}