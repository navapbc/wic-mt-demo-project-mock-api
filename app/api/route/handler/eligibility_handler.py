from typing import Optional
from uuid import uuid4

from pydantic import UUID4, Field

import api.logging
from api.db.models.eligibility_models import EligibilityScreener
from api.util.api_context import ApiContext
from api.util.pydantic_util import PydanticBaseModel

logger = api.logging.get_logger(__name__)


class EligibilityScreenerSharedParams(PydanticBaseModel):
    first_name: str
    last_name: str
    phone_number: str

    # Treat null list the same as empty list by defaulting to empty
    eligibility_categories: list[str] = Field(default_factory=list)
    has_prior_wic_enrollment: bool
    eligibility_programs: list[str] = Field(default_factory=list)

    household_size: Optional[int]
    zip_code: str
    wic_clinic: str
    wic_agency: str
    applicant_notes: Optional[str]


class EligibilityScreenerRequest(EligibilityScreenerSharedParams):
    pass


class EligibilityScreenerResponse(EligibilityScreenerSharedParams):
    eligibility_screener_id: UUID4


def create_eligibility_screener(api_context: ApiContext) -> EligibilityScreenerResponse:
    # Convert & validate the request body
    request = EligibilityScreenerRequest.parse_obj(api_context.request_body)

    # Convert the request body into a DB record
    eligibility_screener = EligibilityScreener(
        # Specify the ID so we don't need to commit + refresh to get from DB
        eligibility_screener_id=uuid4(),
        first_name=request.first_name,
        last_name=request.last_name,
        phone_number=request.phone_number,
        eligibility_categories=request.eligibility_categories,
        has_prior_wic_enrollment=request.has_prior_wic_enrollment,
        eligibility_programs=request.eligibility_programs,
        household_size=request.household_size,
        zip_code=request.zip_code,
        wic_clinic=request.wic_clinic,
        wic_agency=request.wic_agency,
        applicant_notes=request.applicant_notes,
    )

    api_context.db_session.add(eligibility_screener)

    # Convert the DB object to a response
    return EligibilityScreenerResponse.from_orm(eligibility_screener)
