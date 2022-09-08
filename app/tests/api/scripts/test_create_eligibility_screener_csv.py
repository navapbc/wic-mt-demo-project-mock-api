import csv
import os
from datetime import datetime, timezone

import pytest
from smart_open import open as smart_open

from api.db.models.factories import EligibilityScreenerFactory
from api.scripts.create_eligibility_screener_csv import (
    DATETIME_OUTPUT_FORMAT,
    ELIGIBILITY_SCREENER_CSV_HEADER,
    EligiblityScreenerCsvRecord,
    convert_eligibility_screener_records_for_csv,
    create_eligibility_screener_csv,
    get_eligibility_screener_records,
)
from api.util.datetime_util import utcnow
from api.util.file_util import list_files
from api.util.string_utils import blank_for_null, join_list


@pytest.fixture
def tmp_file_path(tmp_path):
    return tmp_path / "example_file.csv"


def read_csv_records(file_path):
    with smart_open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader)
        return csv_rows


def validate_csv_records(db_records, csv_records, test_db_session):
    assert len(csv_records) == len(db_records)

    # Sort the two lists by first name and zip together for validation
    csv_records.sort(key=lambda record: record["First Name"])
    db_records.sort(key=lambda record: record.first_name)
    for csv_record, db_record in zip(csv_records, db_records):
        test_db_session.refresh(db_record)

        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.first_name] == db_record.first_name
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.last_name] == db_record.last_name
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.phone_number] == db_record.phone_number
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.eligibility_categories] == join_list(
            db_record.eligibility_categories
        )
        assert csv_record[
            ELIGIBILITY_SCREENER_CSV_HEADER.has_prior_wic_enrollment
        ] == blank_for_null(db_record.has_prior_wic_enrollment)
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.eligibility_programs] == join_list(
            db_record.eligibility_programs
        )
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.household_size] == blank_for_null(
            db_record.household_size
        )
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.zip_code] == db_record.zip_code
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.chosen_wic_clinic] == "TODO"
        assert csv_record[ELIGIBILITY_SCREENER_CSV_HEADER.applicant_notes] == blank_for_null(
            db_record.applicant_notes
        )
        assert csv_record[
            ELIGIBILITY_SCREENER_CSV_HEADER.submitted_datetime
        ] == db_record.created_at.strftime(DATETIME_OUTPUT_FORMAT)

        # Verify the eligibility screener record  had its timestamp updated
        assert db_record.added_to_eligibility_screener_at is not None
        # and that the timestamp is more than the created_at value (just to show it happened slightly later)
        assert db_record.added_to_eligibility_screener_at > db_record.created_at


def test_create_eligibility_screener_csv_s3(
    test_db_session, initialize_factories_session, mock_s3_bucket
):
    s3_filepath = f"s3://{mock_s3_bucket}/path/to/test.csv"
    db_records = []
    # To make validating these easier in the CSV, make the first names consistent
    db_records.append(
        EligibilityScreenerFactory.create(
            # Routine case
            first_name="A"
        )
    )
    db_records.append(
        EligibilityScreenerFactory.create(
            # Override the factory to flip nullable fields
            first_name="B",
            eligibility_categories=None,
            eligibility_programs=None,
            household_size=5,
            applicant_notes=None,
        )
    )
    db_records.append(
        EligibilityScreenerFactory.create(
            # Multiple records in arrays
            first_name="C",
            eligibility_categories=["baby", "pregnant", "guardian"],
            eligibility_programs=["tanf", "snap", "insurance"],
        )
    )

    create_eligibility_screener_csv(test_db_session, s3_filepath)
    csv_rows = read_csv_records(s3_filepath)
    validate_csv_records(db_records, csv_rows, test_db_session)

    # If we run it again, just a blank file should be made
    create_eligibility_screener_csv(test_db_session, s3_filepath)
    csv_rows = read_csv_records(s3_filepath)
    assert len(csv_rows) == 0

    # If we add another DB record and run it, it'll go in the file
    later_db_records = [EligibilityScreenerFactory.create()]
    create_eligibility_screener_csv(test_db_session, s3_filepath)
    later_csv_rows = read_csv_records(s3_filepath)
    validate_csv_records(later_db_records, later_csv_rows, test_db_session)

    assert "test.csv" in list_files(f"s3://{mock_s3_bucket}/path/to/")


def test_create_eligibility_screener_csv_local(
    test_db_session, initialize_factories_session, tmp_path, tmp_file_path
):
    # Same as above test, but verifying the file
    # logic works locally in addition to S3.
    db_records = [
        EligibilityScreenerFactory.create(first_name="A"),
        EligibilityScreenerFactory.create(first_name="B"),
        EligibilityScreenerFactory.create(first_name="C"),
    ]
    create_eligibility_screener_csv(test_db_session, tmp_file_path)
    csv_rows = read_csv_records(tmp_file_path)
    validate_csv_records(db_records, csv_rows, test_db_session)

    assert os.path.exists(tmp_file_path)


def test_get_eligibility_screener_records(test_db_session, initialize_factories_session):
    # Create some previously processed records we don't expect to find
    EligibilityScreenerFactory.create_batch(3, added_to_eligibility_screener_at=utcnow())

    # Create records and verify they get returned
    unprocessed_records = EligibilityScreenerFactory.create_batch(
        5, added_to_eligibility_screener_at=None
    )
    found_records = get_eligibility_screener_records(test_db_session)
    assert len(found_records) == len(unprocessed_records)
    # Verify its the same records by ID
    assert set([r.eligibility_screener_id for r in found_records]) == set(
        [r.eligibility_screener_id for r in unprocessed_records]
    )


def test_convert_eligibility_screener_records_for_csv():
    # If no records passed in, just the header is returned
    csv_records = convert_eligibility_screener_records_for_csv([])
    assert len(csv_records) == 1
    assert csv_records[0] == ELIGIBILITY_SCREENER_CSV_HEADER

    now = utcnow()
    eligibility_screener = EligibilityScreenerFactory.build(
        eligibility_categories=[],
        has_prior_wic_enrollment=True,
        eligibility_programs=["tanf", "snap"],
        household_size=0,
        applicant_notes="abcd1234",
        created_at=now,
    )
    csv_records = convert_eligibility_screener_records_for_csv([eligibility_screener])
    assert len(csv_records) == 2
    assert csv_records[0] == ELIGIBILITY_SCREENER_CSV_HEADER
    assert csv_records[1] == EligiblityScreenerCsvRecord(
        first_name=eligibility_screener.first_name,
        last_name=eligibility_screener.last_name,
        phone_number=eligibility_screener.phone_number,
        eligibility_categories="",
        has_prior_wic_enrollment="True",
        eligibility_programs="tanf\nsnap",
        household_size="0",
        zip_code=eligibility_screener.zip_code,
        chosen_wic_clinic="TODO",
        applicant_notes="abcd1234",
        submitted_datetime=now.strftime(DATETIME_OUTPUT_FORMAT),
    )


def test_convert_eligibility_screener_records_for_csv_timezone_override(monkeypatch):
    # Make now a static time for testing timezone conversion
    now = datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Set the environment var to make it convert to mountain time
    monkeypatch.setenv("ELIGIBILITY_SCREENER_TIMEZONE", "US/Mountain")

    eligibility_screener = EligibilityScreenerFactory.build(created_at=now)
    csv_records = convert_eligibility_screener_records_for_csv([eligibility_screener])
    assert len(csv_records) == 2
    assert csv_records[0] == ELIGIBILITY_SCREENER_CSV_HEADER
    # Verify the timezone is 7 hours earlier than the UTC time specified above
    assert csv_records[1].submitted_datetime == "01/01/22 05:00 AM"
