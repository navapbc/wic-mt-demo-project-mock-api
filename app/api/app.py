import os

import connexion


def create_app() -> connexion.FlaskApp:

    options = {"swagger_url": "/docs"}
    app = connexion.FlaskApp(
        __name__, specification_dir=get_project_root_dir(), options=options
    )
    app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

    return app


def get_project_root_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..")
