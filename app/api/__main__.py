#!/usr/bin/env python3

# If __main__.py is present in a Python module, it will be executed by default
# if that module is executed, e.g., `python -m my.module`.
#
# https://docs.python.org/3/library/__main__.html

import connexion
import os

def main():
    options = {"swagger_url": "/docs"}
    app = connexion.FlaskApp(__name__, specification_dir=get_project_root_dir(), options=options)
    app.add_api('openapi.yml', strict_validation=True, validate_responses=True)
    app.run(port=8080)

def get_project_root_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..")

main()
