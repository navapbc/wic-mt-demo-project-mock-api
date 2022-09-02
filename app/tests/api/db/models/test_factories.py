import pytest

from api.db.models.eligibility_models import EligibilityScreener
from api.db.models.factories import EligibilityScreenerFactory

# Just validating this is setup correctly
# as the API we have implemented at the moment
# doesn't use it.


def test_eligibility_screener_factory_build():
    # Build doesn't use the DB

    # Build sets the values
    screener = EligibilityScreenerFactory.build()
    assert screener.eligibility_screener_id is not None
    assert screener.first_name is not None
    assert screener.last_name is not None
    assert screener.phone_number is not None

    params = {"first_name": "bob", "last_name": "smith", "phone_number": "123-456-7890"}
    screener = EligibilityScreenerFactory.build(**params)
    for k, v in params.items():
        assert screener.__dict__[k] == v

    params = {"first_name": None, "last_name": None, "phone_number": None}
    screener = EligibilityScreenerFactory.build(**params)
    for k in params.keys():
        assert screener.__dict__[k] is None


def test_factory_create_uninitialized_db_session(test_db_session):
    # DB factory access is disabled from tests unless you add the
    # 'initialize_factories_session' fixture.
    with pytest.raises(Exception, match="DB_FACTORIES_DISABLE_DB_ACCESS is set"):
        EligibilityScreenerFactory.create()


def test_eligibility_screener_factory_create(test_db_session, initialize_factories_session):
    # Create actually writes a record to the DB when run
    # so we'll check the DB directly as well.
    screener = EligibilityScreenerFactory.create()
    assert screener.eligibility_screener_id is not None
    assert screener.first_name is not None
    assert screener.last_name is not None
    assert screener.phone_number is not None

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    assert screener.first_name == db_record.first_name
    assert screener.last_name == db_record.last_name
    assert screener.phone_number == db_record.phone_number

    params = {"first_name": "bob", "last_name": "smith", "phone_number": "123-456-7890"}
    screener = EligibilityScreenerFactory.create(**params)
    for k, v in params.items():
        assert screener.__dict__[k] == v

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    assert screener.first_name == db_record.first_name
    assert screener.last_name == db_record.last_name
    assert screener.phone_number == db_record.phone_number

    params = {"first_name": None, "last_name": None, "phone_number": None}
    screener = EligibilityScreenerFactory.create(**params)
    for k in params.keys():
        assert screener.__dict__[k] is None

    db_record = (
        test_db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.eligibility_screener_id == screener.eligibility_screener_id)
        .one_or_none()
    )
    assert screener.first_name == db_record.first_name
    assert screener.last_name == db_record.last_name
    assert screener.phone_number == db_record.phone_number

    all_db_records = test_db_session.query(EligibilityScreener).all()
    assert len(all_db_records) == 3
