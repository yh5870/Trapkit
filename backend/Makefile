.PHONY: help install dev test lint format db-upgrade db-downgrade db-migrate clean

help: ## 도움말 표시
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 의존성 설치
	pip install -e .

dev: ## 개발 모드로 실행 (자동 리로드)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## 테스트 실행
	pytest

test-cov: ## 테스트 + 커버리지 리포트
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## 린트 실행 (ruff)
	ruff check .

format: ## 포맷팅 (ruff format)
	ruff format .

db-upgrade: ## DB 마이그레이션 적용
	alembic upgrade head

db-downgrade: ## DB 마이그레이션 롤백
	alembic downgrade -1

db-migrate: ## DB 마이그레이션 파일 생성
	alembic revision --autogenerate -m "$(message)"

db-reset: ## DB 초기화
	alembic downgrade base
	alembic upgrade head

clean: ## 임시 파일 삭제
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage