import flask

import api.logging as logging
import api.route.handler.example_person_handler as example_person_handler
import api.util.response as response_util
from api.util.api_context import api_context_manager

logger = logging.get_logger(__name__)


def example_person_post() -> flask.Response:
    """
    POST /v1/example-person
    """
    logger.info("POST /v1/example-person")

    with api_context_manager() as api_context:

        logger.info(api_context.request_body)

        response = example_person_handler.create_example_person(api_context)

        return response_util.success_response(
            message="Success", data=response.dict(), status_code=201
        ).to_api_response()
