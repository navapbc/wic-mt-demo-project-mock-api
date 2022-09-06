from uuid import UUID

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID as postgresUUID
from sqlalchemy.orm import Mapped

from .base import Base, TimestampMixin, uuid_gen


class EligibilityScreener(Base, TimestampMixin):
    __tablename__ = "eligibility_screener"

    eligibility_screener_id: Mapped[UUID] = Column(
        postgresUUID(as_uuid=True), primary_key=True, default=uuid_gen
    )

    # TODO - when the API gets built out, adjust these to handle nullability and format
    first_name = Column(Text)
    last_name = Column(Text)
    phone_number = Column(Text)
