"""username unique

Revision ID: 7fa786180c7b
Revises: d3c56d08ac44
Create Date: 2024-04-15 18:47:56.956101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fa786180c7b'
down_revision = 'd3c56d08ac44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
