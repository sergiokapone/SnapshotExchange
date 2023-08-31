"""add hoto

Revision ID: 8060945f19df
Revises: 0ff47075c7c3
Create Date: 2023-08-31 11:33:27.923282

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8060945f19df'
down_revision: Union[str, None] = '0ff47075c7c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=500), nullable=False),
    sa.Column('photo', sa.String(length=500), nullable=False),
    sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'))
    )
    op.create_foreign_key('fk_user_id', 'posts', 'users', ['user_id'], ['id'])

    op.alter_column('users', 'username', unique=True)  
    op.add_column('users', sa.Column('posts', postgresql.ARRAY(sa.Integer()), nullable=True)) 


def downgrade() -> None:
    op.drop_column('users', 'posts')
    op.alter_column('users', 'username', nullable=True, unique=False) 
    op.drop_table('posts')