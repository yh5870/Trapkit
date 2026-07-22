"""SQLAlchemy Base Model.

이 Base 클래스를 상속받은 모든 ORM 모델은 Alembic 마이그레이션에서
자동으로 감지되어 테이블 스키마가 생성됩니다.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()