import csv
import os
from dataclasses import asdict, dataclass

from smart_open import open as smart_open

import api.db as db
import api.logging
from api.db.models.eligibility_models import EligibilityScreener
from api.scripts.util.script_util import script_context_manager
from api.util.datetime_util import adjust_timezone, utcnow
from api.util.string_utils import blank_for_null, join_list

logger = api.logging.get_logger(__name__)

DATETIME_OUTPUT_FORMAT = "%m/%d/%y %I:%M %p"


@dataclass
class EligiblityScreenerCsvRecord:
    first_name: str
    last_name: str
    phone_number: str
    eligibility_categories: str
    has_prior_wic_enrollment: str
    eligibility_programs: str
    household_size: str
    zip_code: str
    chosen_wic_clinic: str
    applicant_notes: str
    submitted_datetime: str


ELIGIBILITY_SCREENER_CSV_HEADER = EligiblityScreenerCsvRecord(
    first_name="First Name",
    last_name="Last Name",
    phone_number="Phone Number",
    eligibility_categories="Categorical eligibility",
    has_prior_wic_enrollment="Have they or someone in their household been on WIC before?",
    eligibility_programs="Adjunctive eligibility",
    household_size="Household size (only if none of the above for Adjunctive)",  # TODO - do we need that last bit?
    zip_code="Zip Code",
    chosen_wic_clinic="Chosen WIC Clinic",
    applicant_notes="Applicant notes",
    submitted_datetime="Submitted date/time",
)


def create_eligibility_screener_csv(db_session: db.scoped_session, output_file_path: str) -> None:
    # Get DB records
    eligibility_screener_records = get_eligibility_screener_records(db_session)

    # Convert records
    csv_records = convert_eligibility_screener_records_for_csv(eligibility_screener_records)

    # Create file
    generate_csv_file(csv_records, output_file_path)

    # Update DB records with timestamp
    # Only update the timestamp if the file upload worked
    update_db_record_timestamp(eligibility_screener_records)
    db_session.commit()


def get_eligibility_screener_records(db_session: db.scoped_session) -> list[EligibilityScreener]:
    logger.info("Fetching Eligibility Screener records from DB")
    eligibility_screener_records = (
        db_session.query(EligibilityScreener)
        .filter(EligibilityScreener.added_to_eligibility_screener_at == None)  # noqa: E711
        .all()
    )

    record_count = len(eligibility_screener_records)
    logger.info(
        "Found %s eligibility screener records",
        record_count,
        extra={"eligibility_screener_record_count": record_count},
    )

    if record_count == 0:
        logger.warning("No eligibility screener records found that weren't already added to a CSV")

    return eligibility_screener_records


def convert_eligibility_screener_records_for_csv(
    records: list[EligibilityScreener],
) -> list[EligiblityScreenerCsvRecord]:
    logger.info("Converting eligibility screeners to CSV format")
    out_records: list[EligiblityScreenerCsvRecord] = []
    out_records.append(ELIGIBILITY_SCREENER_CSV_HEADER)

    # Env var for adjusting the timezone of the output
    timezone_for_output = os.getenv("ELIGIBILITY_SCREENER_TIMEZONE", "UTC")

    for record in records:
        # Create a timezone in a human-readable format: 09/06/22 05:56 PM
        submitted_datetime = adjust_timezone(record.created_at, timezone_for_output).strftime(
            DATETIME_OUTPUT_FORMAT
        )

        out_record = EligiblityScreenerCsvRecord(
            first_name=record.first_name,
            last_name=record.last_name,
            phone_number=record.phone_number,
            eligibility_categories=join_list(record.eligibility_categories),
            has_prior_wic_enrollment=blank_for_null(record.has_prior_wic_enrollment),
            eligibility_programs=join_list(record.eligibility_programs),
            household_size=blank_for_null(record.household_size),
            zip_code=record.zip_code,
            chosen_wic_clinic=record.wic_clinic,
            applicant_notes=blank_for_null(record.applicant_notes),
            submitted_datetime=submitted_datetime,
        )
        out_records.append(out_record)

    return out_records


def generate_csv_file(records: list[EligiblityScreenerCsvRecord], output_file_path: str) -> None:
    logger.info("Generating eligibility screener CSV at %s", output_file_path)

    # smart_open can write files to local & S3
    with smart_open(output_file_path, "w") as outbound_file:
        csv_writer = csv.DictWriter(
            outbound_file,
            fieldnames=list(asdict(ELIGIBILITY_SCREENER_CSV_HEADER).keys()),
            quoting=csv.QUOTE_ALL,
        )
        for record in records:
            csv_writer.writerow(asdict(record))

    logger.info("Successfully created eligibility screener CSV at %s", output_file_path)


def update_db_record_timestamp(eligibility_screener_records: list[EligibilityScreener]) -> None:
    now = utcnow()

    for record in eligibility_screener_records:
        record.added_to_eligibility_screener_at = now

        logger.info(
            "Updating record %s to have added_to_eligibility_screener_at timestamp %s",
            record.eligibility_screener_id,
            now,
        )


def main() -> None:
    # Initialize DB session / logging / env vars
    with script_context_manager() as script_context:
        # Build the path for the output file
        # This will create a file in the folder specified like:
        # s3://your-bucket/path/to/2022-09-09-12-00-00-eligibility-screener.csv
        # The file path can be either S3 or local disk.
        eligibility_screener_path = os.getenv("ELIGIBILITY_SCREENER_CSV_OUTPUT_PATH", None)
        if not eligibility_screener_path:
            raise Exception("Please specify an ELIGIBILITY_SCREENER_CSV_OUTPUT_PATH env var")

        file_name = utcnow().strftime("%Y-%m-%d-%H-%M-%S") + "-eligibility-screener.csv"
        output_file_path = os.path.join(eligibility_screener_path, file_name)

        create_eligibility_screener_csv(script_context.db_session, output_file_path)
