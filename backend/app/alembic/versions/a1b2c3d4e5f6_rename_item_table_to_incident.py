"""Rename item table to incident

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-02-16 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("item", "incident")


def downgrade():
    op.rename_table("incident", "item")
