import connexion

import api.app as app
import api.logging as logging
import api.util.response as response_util
from api.db.models.eligibility_models import EligibilityScreener

logger = logging.get_logger(__name__)


def eligibility_screener_post():
    body = connexion.request.json

    logger.info(body)

    with app.db_session() as db_session:

        # TODO - when I add Pydantic in the next ticket
        # we'll use that
        eligibility_screener = EligibilityScreener(
            first_name=body["first_name"],
            last_name=body["last_name"],
            phone_number=body["phone_number"],
        )
        db_session.add(eligibility_screener)
        db_session.commit()

    return response_util.success_response(
        message="It was a success",
        data=body,  # TODO - Echo it back for the moment - in Pydantic PR build from DB object
        status_code=201,
    ).to_api_response()
