"""Remove extra columns

Revision ID: 07a5eb084ad9
Revises: 491626237bb1
Create Date: 2022-03-25 18:15:05.012969

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '07a5eb084ad9'
down_revision = '491626237bb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('authors', 'date_created')
    op.drop_column('publishers', 'date_created')
    op.drop_column('series', 'date_created')
    op.drop_column('series', 'index')
    op.drop_column('tags', 'date_created')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tags', sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('series', sa.Column('index', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('series', sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('publishers', sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('authors', sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###