"""Baggage Rules Seed Data

수화물 규정 데이터베이스 시드 파일
항공사별 수화물 규정 (25개 규칙)
"""

revision = '20260723_1453'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # 수화물 규정 테이블 생성
    op.create_table(
        'baggage_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('item_key', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('aliases', sa.JSON(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('carry_on_rule', sa.JSON(), nullable=False),
        sa.Column('checked_rule', sa.JSON(), nullable=False),
        sa.Column('tips', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), server_default='iata', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_key')
    )
    op.create_index('idx_baggage_rules_item_key', 'baggage_rules', ['item_key'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_baggage_rules_item_key', table_name='baggage_rules')
    op.drop_table('baggage_rules')