"""added link table

Revision ID: bfd35ebcbeb5
Revises: 
Create Date: 2020-01-30 21:29:35.727874+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfd35ebcbeb5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'phlasch_db_link',
        sa.Column(
            'id',
            sa.Integer,
            primary_key=True,
        ),
        sa.Column(
            'address',
            sa.Text,
            sa.CheckConstraint("address>''"),
            nullable=False,
        ),
        sa.Column(
            'shortcut',
            sa.String(256),
            nullable=True,
            unique=True,
            index=True,
        ),
        sa.Column(
            'visits',
            sa.Integer,
            nullable=False,
            server_default="0",
        ),
    )


def downgrade():
    op.drop_table('phlasch_db_link')
