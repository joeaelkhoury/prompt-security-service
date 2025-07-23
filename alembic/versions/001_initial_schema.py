"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # User profiles table
    op.create_table('user_profiles',
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('reputation_score', sa.Float(), nullable=True),
        sa.Column('total_prompts', sa.Integer(), nullable=True),
        sa.Column('blocked_prompts', sa.Integer(), nullable=True),
        sa.Column('suspicious_patterns', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index('idx_reputation', 'user_profiles', ['reputation_score'])
    
    # Prompts table
    op.create_table('prompts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sanitized_content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('safety_score', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_timestamp', 'prompts', ['user_id', 'timestamp'])
    op.create_index(op.f('ix_prompts_status'), 'prompts', ['status'])
    op.create_index(op.f('ix_prompts_user_id'), 'prompts', ['user_id'])
    
    # Similarities table
    op.create_table('similarities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('prompt1_id', sa.String(36), nullable=True),
        sa.Column('prompt2_id', sa.String(36), nullable=True),
        sa.Column('metric', sa.String(50), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prompt1_id'], ['prompts.id'], ),
        sa.ForeignKeyConstraint(['prompt2_id'], ['prompts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_similarity_lookup', 'similarities', ['prompt1_id', 'prompt2_id'])

def downgrade():
    op.drop_index('idx_similarity_lookup', table_name='similarities')
    op.drop_table('similarities')
    op.drop_index(op.f('ix_prompts_user_id'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_status'), table_name='prompts')
    op.drop_index('idx_user_timestamp', table_name='prompts')
    op.drop_table('prompts')
    op.drop_index('idx_reputation', table_name='user_profiles')
    op.drop_table('user_profiles')