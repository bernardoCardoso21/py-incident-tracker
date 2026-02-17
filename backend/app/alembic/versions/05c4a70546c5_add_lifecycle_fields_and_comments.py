"""add lifecycle fields and comments

Revision ID: 05c4a70546c5
Revises: a1b2c3d4e5f6
Create Date: 2026-02-17 18:33:02.654549

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '05c4a70546c5'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Create PostgreSQL enum types first
    incidentstatus = sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED', name='incidentstatus')
    incidentpriority = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='incidentpriority')
    incidentcategory = sa.Enum('BUG', 'FEATURE_REQUEST', 'QUESTION', 'DOCUMENTATION', name='incidentcategory')
    incidentstatus.create(op.get_bind(), checkfirst=True)
    incidentpriority.create(op.get_bind(), checkfirst=True)
    incidentcategory.create(op.get_bind(), checkfirst=True)

    # Create comment table
    op.create_table('comment',
    sa.Column('content', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('incident_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['incident_id'], ['incident.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Add lifecycle columns to incident table
    op.add_column('incident', sa.Column('status', incidentstatus, nullable=False, server_default='OPEN'))
    op.add_column('incident', sa.Column('priority', incidentpriority, nullable=False, server_default='MEDIUM'))
    op.add_column('incident', sa.Column('category', incidentcategory, nullable=False, server_default='BUG'))
    op.add_column('incident', sa.Column('assignee_id', sa.Uuid(), nullable=True))
    op.add_column('incident', sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key(None, 'incident', 'user', ['assignee_id'], ['id'], ondelete='SET NULL')


def downgrade():
    op.drop_constraint(None, 'incident', type_='foreignkey')
    op.drop_column('incident', 'resolved_at')
    op.drop_column('incident', 'assignee_id')
    op.drop_column('incident', 'category')
    op.drop_column('incident', 'priority')
    op.drop_column('incident', 'status')
    op.drop_table('comment')

    # Drop enum types
    sa.Enum(name='incidentcategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='incidentstatus').drop(op.get_bind(), checkfirst=True)
