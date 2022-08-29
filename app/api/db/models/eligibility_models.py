from .base import Base, TimestampMixin, uuid_gen
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

class EligibilityScreener(Base, TimestampMixin):
    __tablename__ = "eligibility_screener"

    # TODO - check if the UUID mypy issue is fixed with 1.4
    eligibility_screener_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)

    # TODO - when the API gets built out, adjust these to handle nullability and format
    first_name = Column(Text)
    last_name = Column(Text)
    phone_number = Column(Text)