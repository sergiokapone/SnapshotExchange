"""add cloud_public_id field

Revision ID: 01e60cf45289
Revises: 58028d0c017e
Create Date: 2023-09-05 01:17:11.164143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01e60cf45289'
down_revision: Union[str, None] = '58028d0c017e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photos', sa.Column('cloud_public_id', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('photos', 'cloud_public_id')
    # ### end Alembic commands ###
