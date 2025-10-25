"""Add game state tables

Revision ID: 2a8b7c9d3e1f
Revises: 1a73ac545ec4
Create Date: 2025-10-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '2a8b7c9d3e1f'
down_revision: Union[str, None] = '1a73ac545ec4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('last_played_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('turn_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_location_id', sa.String(), nullable=True),
        sa.Column('state_snapshot', sa.JSON(), nullable=True),
        sa.Column('current_quest', sa.Text(), nullable=True),
        sa.Column('quest_progress', sa.JSON(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=False),
        sa.Column('ai_model', sa.String(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_sessions_id'), 'game_sessions', ['id'], unique=False)

    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('char_class', sa.String(), nullable=False),
        sa.Column('team', sa.String(), nullable=False),
        sa.Column('hp', sa.Integer(), nullable=False),
        sa.Column('max_hp', sa.Integer(), nullable=False),
        sa.Column('mana', sa.Integer(), nullable=False),
        sa.Column('max_mana', sa.Integer(), nullable=False),
        sa.Column('attack', sa.Integer(), nullable=False),
        sa.Column('defense', sa.Integer(), nullable=False),
        sa.Column('ability_scores', sa.JSON(), nullable=False),
        sa.Column('alive', sa.Boolean(), nullable=False),
        sa.Column('current_location_id', sa.String(), nullable=True),
        sa.Column('status_effects', sa.JSON(), nullable=False),
        sa.Column('inventory', sa.JSON(), nullable=False),
        sa.Column('spells', sa.JSON(), nullable=False),
        sa.Column('proficiency_bonus', sa.Integer(), nullable=False),
        sa.Column('skill_proficiencies', sa.JSON(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_characters_id'), 'characters', ['id'], unique=False)
    op.create_index(op.f('ix_characters_session_id'), 'characters', ['session_id'], unique=False)
    op.create_index(op.f('ix_characters_name'), 'characters', ['name'], unique=False)

    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_type', sa.String(), nullable=False),
        sa.Column('connections', sa.JSON(), nullable=False),
        sa.Column('npcs', sa.JSON(), nullable=False),
        sa.Column('services', sa.JSON(), nullable=False),
        sa.Column('encounter_chance', sa.Integer(), nullable=False),
        sa.Column('encounter_types', sa.JSON(), nullable=False),
        sa.Column('visited', sa.Integer(), nullable=False),
        sa.Column('cleared', sa.Integer(), nullable=False),
        sa.Column('character_ids', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index(op.f('ix_locations_session_id'), 'locations', ['session_id'], unique=False)
    op.create_index(op.f('ix_locations_name'), 'locations', ['name'], unique=False)

    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_id', sa.String(), nullable=True),
        sa.Column('character_ids', sa.JSON(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('state_before', sa.JSON(), nullable=True),
        sa.Column('state_after', sa.JSON(), nullable=True),
        sa.Column('checksum', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_session_id'), 'events', ['session_id'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_turn_number'), 'events', ['turn_number'], unique=False)
    op.create_index(op.f('ix_events_location_id'), 'events', ['location_id'], unique=False)
    op.create_index(op.f('ix_events_created_at'), 'events', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index(op.f('ix_events_created_at'), table_name='events')
    op.drop_index(op.f('ix_events_location_id'), table_name='events')
    op.drop_index(op.f('ix_events_turn_number'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_session_id'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')

    op.drop_index(op.f('ix_locations_name'), table_name='locations')
    op.drop_index(op.f('ix_locations_session_id'), table_name='locations')
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.drop_table('locations')

    op.drop_index(op.f('ix_characters_name'), table_name='characters')
    op.drop_index(op.f('ix_characters_session_id'), table_name='characters')
    op.drop_index(op.f('ix_characters_id'), table_name='characters')
    op.drop_table('characters')

    op.drop_index(op.f('ix_game_sessions_id'), table_name='game_sessions')
    op.drop_table('game_sessions')
