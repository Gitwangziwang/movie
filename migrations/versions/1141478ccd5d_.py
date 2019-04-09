"""empty message

Revision ID: 1141478ccd5d
Revises: c34aad6be4af
Create Date: 2019-04-02 11:57:40.667245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1141478ccd5d'
down_revision = 'c34aad6be4af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_admin_add_time', table_name='admin')
    op.drop_index('name', table_name='admin')
    op.drop_table('admin')
    op.add_column('user', sa.Column('role_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role_id')
    op.create_table('admin',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('is_super', mysql.SMALLINT(display_width=6), autoincrement=False, nullable=True),
    sa.Column('add_time', mysql.DATETIME(), nullable=True),
    sa.Column('password', mysql.VARCHAR(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'admin', ['name'], unique=True)
    op.create_index('ix_admin_add_time', 'admin', ['add_time'], unique=False)
    # ### end Alembic commands ###