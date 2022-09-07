import pytest

from api.db.models.eligibility_models import EligibilityScreener
from api.db.models.factories import EligibilityScreenerFactory

# Just validating this is setup correctly
# as the API we have implemented at the moment
# doesn't use it.

params = {
    "first_name": "bob",
    "last_name": "smith",
    "phone_number": "123-456-7890",
    "eligibility_categories": ["pregnant"],
    "has_prior_wic_enrollment": True,
    "eligibility_programs": ["tanf", "snap"],
    "household_size": 3,
    "zip_code": "12345-6789",
    "wic_clinic": "example clinic",
    "applicant_notes": "notes?",
}


def validate_screener_record(screener, expected_values=None):
    # Grab the JSON of the screener for easy access
    if expected_values:
        screener_json = screener.for_json()
        assert screener.eligibility_screener_id is not None
        for k, v in expected_values.items():
            assert screener_json[k] == v
    else:
        # Otherwise just validate the values are set
        assert screener.eligibility_screener_id is not None
        assert screener.first_name is not None
        assert screener.last_name is not None
        assert screener.phone_number is not None
        assert (
            screener.eligibility_categories is not None and len(screener.eligibility_categories) > 0
        )
        assert screener.has_prior_wic_enrollment is not None
        assert screener.eligibility_programs is not None and len(screener.eligibility_programs) > 0
        assert screener.household_size is None  # The default
        assert screener.zip_code is not None
        assert screener.applicant_notes is not None


def test_eligibility_screener_factory_build():
    # Build doesn't use the DB

    # Build sets the values
    screener = EligibilityScreenerFactory.build()
    validate_screener_record(screener)

    screener = EligibilityScreenerFactory.build(**params)
    validate_screener_record(screener, params)


def test_factory_create_uninitialized_db_session(test_db_session):
    # DB factory access is disabled from tests unless you add the
    # 'initialize_factories_session' fixture.
    with pytest.raises(Exception, match="DB_FACTORIES_DISABLE_DB_ACCESS is set"):
        EligibilityScreenerFactory.create()


def test_eligibility_screener_factory_create(test_db_session, initialize_factories_session):
    # Create actually writes a record to the DB when run
    # so we'll check the DB directly as well.
    screener = EligibilityScreenerFactory.create()
    validate_screener_record(screener)

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    # Make certain the DB record matches the factory one.
    validate_screener_record(db_record, screener.for_json())

    screener = EligibilityScreenerFactory.create(**params)
    validate_screener_record(screener, params)

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    # Make certain the DB record matches the factory one.
    validate_screener_record(db_record, screener.for_json())

    # Can set nullable values, overriding any default
    null_params = {
        "eligibility_categories": None,
        "eligibility_programs": None,
        "household_size": None,
        "applicant_notes": None,
    }
    screener = EligibilityScreenerFactory.create(**null_params)
    validate_screener_record(screener, null_params)

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    validate_screener_record(db_record, screener.for_json())

    all_db_records = test_db_session.query(EligibilityScreener).all()
    assert len(all_db_records) == 3
