from uuid import uuid4

from pydantic import UUID4

import api.logging
from api.db.models.eligibility_models import EligibilityScreener
from api.util.api_context import ApiContext
from api.util.pydantic_util import PydanticBaseModel

logger = api.logging.get_logger(__name__)


class EligibilityScreenerSharedParams(PydanticBaseModel):
    first_name: str
    last_name: str
    phone_number: str


class EligibilityScreenerRequest(EligibilityScreenerSharedParams):
    pass


class EligibilityScreenerResponse(EligibilityScreenerSharedParams):
    eligibility_screener_id: UUID4


def create_eligibility_screener(api_context: ApiContext) -> EligibilityScreenerResponse:
    # TODO - the code this is based on does a lot of this in the
    # API itself but I've always found that hard to read, so
    # moving a lot more to this handler. Need to see how
    # well that works out as more is added.
    request = EligibilityScreenerRequest.parse_obj(api_context.request_body)
    logger.info(request)  # TODO - remove, just for testing at the moment

    eligibility_screener = EligibilityScreener(
        # Specify the ID so we don't need to commit + refresh to get from DB
        eligibility_screener_id=uuid4(),
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
    )

    api_context.db_session.add(eligibility_screener)

    return EligibilityScreenerResponse.from_orm(eligibility_screener)
