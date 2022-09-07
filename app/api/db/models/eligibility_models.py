from uuid import UUID

from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as postgresUUID
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped

from .base import Base, TimestampMixin, uuid_gen


class EligibilityScreener(Base, TimestampMixin):
    __tablename__ = "eligibility_screener"

    eligibility_screener_id: Mapped[UUID] = Column(
        postgresUUID(as_uuid=True), primary_key=True, default=uuid_gen
    )

    first_name: str = Column(Text, nullable=False)
    last_name: str = Column(Text, nullable=False)
    phone_number: str = Column(Text, nullable=False)
    # MutableList wraps these arrays so mutations on the python
    # object array (eg. add()) get detected by the array.
    # See: https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.ARRAY
    eligibility_categories: list[str] = Column(MutableList.as_mutable(ARRAY(Text)), nullable=True)
    has_prior_wic_enrollment = Column(Boolean, nullable=False)
    eligibility_programs: list[str] = Column(MutableList.as_mutable(ARRAY(Text)), nullable=True)
    household_size = Column(Integer, nullable=True)
    zip_code: str = Column(Text, nullable=False)
    wic_clinic: str = Column(Text, nullable=False)
    applicant_notes = Column(Text, nullable=True)

    added_to_eligibility_screener_at = Column(TIMESTAMP(timezone=True), nullable=True)
