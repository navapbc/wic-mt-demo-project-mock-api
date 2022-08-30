import pytest

import api.app as app_entry


@pytest.fixture
def app():
    return app_entry.create_app()


@pytest.fixture
def client(app):
    return app.app.test_client()

