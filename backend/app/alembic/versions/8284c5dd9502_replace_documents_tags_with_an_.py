"""Replace documents tags with an association table

Revision ID: 8284c5dd9502
Revises: 8d976d43a9d7
Create Date: 2024-12-17 18:46:48.149682

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '8284c5dd9502'
down_revision = '8d976d43a9d7'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the primary key constraint (likely named document_tags_pkey)
    op.drop_constraint('document_tags_pkey', 'document_tags', type_='primary')
    
    # Drop the index on id
    op.drop_index('ix_document_tags_id', table_name='document_tags')
    
    # Drop the id column
    op.drop_column('document_tags', 'id')
    
    # Ensure document_id and tag_id are non-nullable 
    op.alter_column('document_tags', 'document_id', existing_type=sa.Integer, nullable=False)
    op.alter_column('document_tags', 'tag_id', existing_type=sa.Integer, nullable=False)
    
    # Now create a new primary key constraint on (document_id, tag_id)
    op.create_primary_key("pk_document_tags", "document_tags", ["document_id", "tag_id"])


def downgrade():
    # Drop the composite primary key
    op.drop_constraint("pk_document_tags", "document_tags", type_='primary')

    # Revert columns to nullable
    op.alter_column('document_tags', 'tag_id', existing_type=sa.Integer, nullable=True)
    op.alter_column('document_tags', 'document_id', existing_type=sa.Integer, nullable=True)
    
    # Add back the id column
    op.add_column('document_tags', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    
    # Recreate the original primary key constraint on id
    op.create_primary_key('document_tags_pkey', 'document_tags', ['id'])
    
    # Recreate the index on id
    op.create_index('ix_document_tags_id', 'document_tags', ['id'], unique=False)
