import os
import uuid
from dataclasses import dataclass
from typing import Any

import flask
from werkzeug.exceptions import Unauthorized

import api.logging

logger = api.logging.get_logger(__name__)


@dataclass
class User:
    # WARNING: This is a very rudimentary
    # user for demo purposes and is not
    # a production ready approach. It exists
    # purely to define a rough structure / example
    user_id: uuid.UUID
    sub_id: str
    username: str

    def as_dict(self):
        # Connexion expects a dictionary it can
        # use .get() on, so convert this to that format
        return {"uid": self.user_id, "sub": self.sub_id}


API_AUTH_USER = User(uuid.uuid4(), "sub_id_1234", "API auth user")


def api_key_auth(token: str, required_scopes: Any) -> User:
    logger.info("Authenticating provided token")

    user = process_token(token)
    flask.g.current_user = user

    logger.info("Authentication successful", extra={"user_id": user.user_id})

    return user.as_dict()


def process_token(token: str) -> User:
    # WARNING: this isn't really a production ready
    # auth approach. In reality the user object returned
    # here should be pulled from a DB or auth service, but
    # as there are several types of authentication, we are
    # keeping this pretty basic for the out-of-the-box approach
    expected_auth_token = os.getenv("API_AUTH_TOKEN", None)

    if not expected_auth_token:
        logger.info(
            "Authentication is not setup, please add an API_AUTH_TOKEN environment variable."
        )
        raise Unauthorized(
            "Authentication is not setup properly and the user cannot be authenticated"
        )

    if token != expected_auth_token:
        logger.info("Authentication failed for provided auth token.")
        raise Unauthorized

    return API_AUTH_USER
