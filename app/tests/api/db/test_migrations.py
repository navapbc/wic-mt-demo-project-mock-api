import pytest
from alembic import command
from alembic.script import ScriptDirectory
from alembic.script.revision import MultipleHeads
from alembic.util.exc import CommandError

import api.db
from api.db.migrations.run import alembic_cfg
from tests.conftest import db_schema_create, db_schema_drop


def test_only_single_head_revision_in_migrations():
    script = ScriptDirectory.from_config(alembic_cfg)

    try:
        # This will raise if there are multiple heads
        script.get_current_head()
        multihead_situation = False
    except CommandError as e:
        # re-raise anything not expected
        if not isinstance(e.__cause__, MultipleHeads):
            raise

        multihead_situation = True

    # raising assertion error here instead of in `except` block to avoid pytest
    # printing the huge stacktrace of the multi-head exception, which in this
    # case we don't really care about the details, just using it as a flag
    if multihead_situation:
        raise AssertionError(
            "Multi-head migration issue: run `make db-migrate-merge-heads` to resolve"
        )


@pytest.fixture
def test_db_schema_non_session(monkeypatch):
    """
    Create a test schema, if it doesn't already exist, and drop it after the
    test completes.

    The monkeypatch setup of the test_db_schema fixture causes this issues
    so copied here with that adjusted
    """
    schema_name = "mock_api_test_non_session_test_1234"

    monkeypatch.setenv("DB_SCHEMA", schema_name)
    monkeypatch.setenv("POSTGRES_DB", "mock-api")
    monkeypatch.setenv("POSTGRES_USER", "mock_api_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret123")
    monkeypatch.setenv("ENVIRONMENT", "local")

    db_schema_create(schema_name)
    try:
        yield schema_name
    finally:
        db_schema_drop(schema_name)


def test_db_setup_via_alembic_migration(test_db_schema_non_session):
    # Change directory location so the relative script_location in alembic config works.
    command.upgrade(alembic_cfg, "head")


def test_db_init_with_migrations(test_db_schema_non_session):
    # Verify the DB session works after initializing the migrations
    db_session = api.db.init()

    db_session.close()
    db_session.remove()