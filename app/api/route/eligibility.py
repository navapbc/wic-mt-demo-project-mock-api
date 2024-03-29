import flask

import api.logging as logging
import api.route.handler.eligibility_handler as eligibility_handler
import api.util.response as response_util
from api.util.api_context import api_context_manager

logger = logging.get_logger(__name__)


def eligibility_screener_post() -> flask.Response:
    """
    POST /v1/eligibility-screener
    """
    logger.info("POST /v1/eligibility-screener")

    with api_context_manager() as api_context:

        response = eligibility_handler.create_eligibility_screener(api_context)

        api_context.db_session.commit()

        log_extra = api_context.get_log_extra() | {
            "eligibility_screener_id": response.eligibility_screener_id
        }
        logger.info("Successfully submitted eligibility screener", extra=log_extra)

        return response_util.success_response(
            message="Added eligibility screener to DB",
            data=response.dict(),
            status_code=201,
        ).to_api_response()
