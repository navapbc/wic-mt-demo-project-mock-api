from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as postgresUUID, ARRAY
from sqlalchemy.orm import Mapped
from .base import Base, TimestampMixin, uuid_gen
from sqlalchemy.ext.mutable import MutableList


class EligibilityScreener(Base, TimestampMixin):
    __tablename__ = "eligibility_screener"

    eligibility_screener_id: Mapped[UUID] = Column(
        postgresUUID(as_uuid=True), primary_key=True, default=uuid_gen
    )

    # TODO - when the API gets built out, adjust these to handle nullability and format
    first_name = Column(Text)
    last_name = Column(Text)
    phone_number = Column(Text)
    # MutableList wraps these arrays so mutations on the python
    # object array (eg. add()) get detected by the array.
    # See: https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.ARRAY
    eligibility_categories = Column(MutableList.as_mutable(ARRAY(Text)))
    has_prior_wic_enrollment = Column(Boolean)
    eligibility_programs = Column(MutableList.as_mutable(ARRAY(Text)))
    household_size = Column(Integer, nullable=True)
    zip_code = Column(Text)
    applicant_notes = Column(Text, nullable=True)
