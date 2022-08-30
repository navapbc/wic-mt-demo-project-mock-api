import connexion

import api.logging as logging
import api.util.response as response_util

logger = logging.get_logger(__name__)


def eligibility_screener_post():
    body = connexion.request.json

    logger.info(body)

    return response_util.success_response(
        message="It was a success",
        data=body,  # Echo it back for the moment
        status_code=201,
    ).to_api_response()
