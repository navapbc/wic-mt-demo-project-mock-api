import flask

import api.handler.eligibility_handler as eligibility_handler
import api.logging as logging
import api.util.response as response_util
from api.util.api_context import api_context_manager

logger = logging.get_logger(__name__)


def eligibility_screener_post() -> flask.Response:
    """
    POST /v1/eligibility-screener
    """

    with api_context_manager() as api_context:
        response = eligibility_handler.create_eligibility_screener(api_context)

        api_context.db_session.commit()

        return response_util.success_response(
            message="Added eligibility screener to DB",
            data=response.dict(),
            status_code=201,
        ).to_api_response()
