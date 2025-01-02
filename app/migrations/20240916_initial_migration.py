"""dev_migration

Revision ID: 175a4096e46d
Revises: 
Create Date: 2024-12-23 10:32:58.420683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '175a4096e46d'
down_revision = None
branch_labels = ('default',)
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ab_permission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "ab_register_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password", sa.String(length=256), nullable=True),
        sa.Column("email", sa.String(length=64), nullable=False),
        sa.Column("registration_date", sa.DateTime(), nullable=True),
        sa.Column("registration_hash", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "ab_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "ab_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password", sa.String(length=256), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("login_count", sa.Integer(), nullable=True),
        sa.Column("fail_login_count", sa.Integer(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.Column("changed_on", sa.DateTime(), nullable=True),
        sa.Column("created_by_fk", sa.Integer(), nullable=True),
        sa.Column("changed_by_fk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["changed_by_fk"],
            ["ab_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_fk"],
            ["ab_user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "ab_view_menu",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "ab_permission_view",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=True),
        sa.Column("view_menu_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["ab_permission.id"],
        ),
        sa.ForeignKeyConstraint(
            ["view_menu_id"],
            ["ab_view_menu.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("permission_id", "view_menu_id"),
    )
    op.create_table(
        "ab_user_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["ab_role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["ab_user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id"),
    )
    op.create_table(
        "ab_permission_view_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("permission_view_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["permission_view_id"],
            ["ab_permission_view.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["ab_role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("permission_view_id", "role_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("ab_permission_view_role")
    op.drop_table("ab_user_role")
    op.drop_table("ab_permission_view")
    op.drop_table("ab_view_menu")
    op.drop_table("ab_user")
    op.drop_table("ab_role")
    op.drop_table("ab_register_user")
    op.drop_table("ab_permission")
    # ### end Alembic commands ###