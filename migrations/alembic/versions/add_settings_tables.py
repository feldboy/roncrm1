"""Add settings tables

Revision ID: add_settings_tables
Revises: 
Create Date: 2025-07-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_settings_tables'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Create settings_categories table
    op.create_table('settings_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_categories_id'), 'settings_categories', ['id'], unique=False)
    op.create_index(op.f('ix_settings_categories_name'), 'settings_categories', ['name'], unique=True)

    # Create settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=200), nullable=False),
        sa.Column('display_name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=50), nullable=False),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('current_value', sa.Text(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('ui_component', sa.String(length=50), nullable=True),
        sa.Column('ui_options', sa.JSON(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=True),
        sa.Column('is_readonly', sa.Boolean(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('requires_restart', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['settings_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_id'), 'settings', ['id'], unique=False)
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=False)
    op.create_index('idx_settings_category_key', 'settings', ['category_id', 'key'], unique=False)
    op.create_index('idx_settings_active', 'settings', ['is_active'], unique=False)

    # Create user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('setting_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['setting_id'], ['settings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_settings_id'), 'user_settings', ['id'], unique=False)
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=False)
    op.create_index('idx_user_settings_user_setting', 'user_settings', ['user_id', 'setting_id'], unique=True)

    # Create agent_settings table
    op.create_table('agent_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('agent_id', sa.String(length=100), nullable=True),
        sa.Column('setting_key', sa.String(length=200), nullable=False),
        sa.Column('setting_value', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(length=50), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('validation_schema', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_settings_id'), 'agent_settings', ['id'], unique=False)
    op.create_index(op.f('ix_agent_settings_agent_type'), 'agent_settings', ['agent_type'], unique=False)
    op.create_index(op.f('ix_agent_settings_agent_id'), 'agent_settings', ['agent_id'], unique=False)
    op.create_index('idx_agent_settings_type_key', 'agent_settings', ['agent_type', 'setting_key'], unique=False)
    op.create_index('idx_agent_settings_instance', 'agent_settings', ['agent_id', 'setting_key'], unique=False)

    # Create settings_audit_log table
    op.create_table('settings_audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setting_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('change_reason', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['setting_id'], ['settings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_audit_log_id'), 'settings_audit_log', ['id'], unique=False)
    op.create_index(op.f('ix_settings_audit_log_user_id'), 'settings_audit_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_settings_audit_log_created_at'), 'settings_audit_log', ['created_at'], unique=False)

    # Create settings_profiles table
    op.create_table('settings_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('settings_data', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_profiles_id'), 'settings_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_settings_profiles_name'), 'settings_profiles', ['name'], unique=True)


def downgrade():
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('settings_profiles')
    op.drop_table('settings_audit_log')
    op.drop_table('agent_settings')
    op.drop_table('user_settings')
    op.drop_table('settings')
    op.drop_table('settings_categories')