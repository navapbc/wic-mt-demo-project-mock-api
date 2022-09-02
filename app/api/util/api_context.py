from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator

import connexion

import api.app as app
import api.db as db


@dataclass
class ApiContext:
    """
    Container class for components that most
    API endpoints need, grouped so we can avoid
    the boilerplate of fetching all of these
    """

    request_body: Any
    current_user: Any  # TODO - type
    db_session: db.scoped_session


@contextmanager
def api_context_manager() -> Generator[ApiContext, None, None]:
    """
    API context manager for working with
    requests and processing them to the DB.

    Sets up the DB session, current user,
    and grabs the request body.
    """
    with app.db_session() as db_session:
        # TODO - verify this works with requests that don't have a body
        body = connexion.request.json
        # TODO - current user will be relevant when we get to auth
        current_user = app.current_user()

        yield ApiContext(body, current_user, db_session)
