"""dev_migration

Revision ID: ce740692af1e
Revises: 175a4096e46d
Create Date: 2024-09-16 22:39:48.385997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce740692af1e'
down_revision = '175a4096e46d'
branch_labels = ()
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('city_locations',
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.Column('changed_on', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city_name', sa.String(length=512), nullable=True),
    sa.Column('latitude', sa.DECIMAL(precision=8, scale=7), nullable=True),
    sa.Column('longitude', sa.DECIMAL(precision=8, scale=7), nullable=True),
    sa.Column('created_by_fk', sa.Integer(), nullable=False),
    sa.Column('changed_by_fk', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
    sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('city_locations')
    # ### end Alembic commands ###
