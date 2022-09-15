import faker
from api.db.models.eligibility_models import EligibilityScreener

fake = faker.Faker()

base_request = {
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "phone_number": "123-456-7890",
    "eligibility_categories": ["baby", "pregnant"],
    "has_prior_wic_enrollment": False,
    "eligibility_programs": ["tanf"],
    "household_size": None,
    "zip_code": "12345",
    "wic_clinic": "Example Clinic\n1234 Main Street Cityville, MT 12345",
    "applicant_notes": "example_notes",
}


def test_post_eligibility_201(client, api_auth_token, test_db_session):
    request = base_request | {}
    response = client.post(
        "/v1/eligibility-screener", json=request, headers={"X-Auth": api_auth_token}
    )

    assert response.status_code == 201

    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 1
    db_eligibility_screener = results[0]
    response_eligibility_screener = response.get_json()["data"]

    # Verify the request, response and DB model values all match
    for k in request:
        assert response_eligibility_screener[k] == request[k]
        assert db_eligibility_screener.__dict__[k] == request[k]

    # Verify the IDs were set properly
    assert db_eligibility_screener.eligibility_screener_id is not None
    assert (
        str(db_eligibility_screener.eligibility_screener_id)
        == response_eligibility_screener["eligibility_screener_id"]
    )


def test_post_eligibility_201_empty_arrays(client, api_auth_token, test_db_session):
    # Verify that null and empty arrays for the enums behave the same.
    request = base_request | {
        "eligibility_categories": [],
        "eligibility_programs": [],
    }
    response = client.post(
        "/v1/eligibility-screener", json=request, headers={"X-Auth": api_auth_token}
    )

    assert response.status_code == 201

    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 1
    db_eligibility_screener = results[0]
    response_eligibility_screener = response.get_json()["data"]

    # Verify the request, response and DB model values all match
    for k in request:
        assert response_eligibility_screener[k] == request[k]
        assert db_eligibility_screener.__dict__[k] == request[k]

    # Verify the IDs were set properly
    assert db_eligibility_screener.eligibility_screener_id is not None
    assert (
        str(db_eligibility_screener.eligibility_screener_id)
        == response_eligibility_screener["eligibility_screener_id"]
    )


def test_post_eligibility_400_missing_required_fields(client, api_auth_token, test_db_session):
    # Send an empty post - should fail validation
    response = client.post("/v1/eligibility-screener", json={}, headers={"X-Auth": api_auth_token})
    assert response.status_code == 400

    error_list = response.get_json()["errors"]
    required_fields = [
        "first_name",
        "last_name",
        "phone_number",
        "has_prior_wic_enrollment",
        "zip_code",
        "wic_clinic",
    ]
    assert len(error_list) == len(
        required_fields
    ), f"Errored fields don't match expected for empty request {error_list}"
    for error in error_list:
        field, message, error_type = error["field"], error["message"], error["type"]
        assert field in required_fields
        assert "Field required" in message
        assert error_type == "value_error.missing"

    # Nothing added to DB
    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 0


def test_post_eligibility_400_invalid_types(client, api_auth_token, test_db_session):
    request = {
        "first_name": 1,
        "last_name": 2,
        "phone_number": 3,
        "eligibility_categories": 4,
        "has_prior_wic_enrollment": 5,
        "eligibility_programs": 6,
        "household_size": "text",
        "zip_code": 7,
        "applicant_notes": 8,
    }
    response = client.post(
        "/v1/eligibility-screener", json=request, headers={"X-Auth": api_auth_token}
    )

    assert response.status_code == 400
    error_list = response.get_json()["errors"]
    # We expect the errors to be in a dict like:
    # {
    #   'field': 'eligibility_categories',
    #   'message': "4 is not of type 'array'",
    #   'rule': 'array',
    #   'type': 'type',
    #   'value': 'int'
    # }
    for error in error_list:
        field, message, error_type, incorrect_type = (
            error["field"],
            error["message"],
            error["type"],
            error["value"],
        )
        assert field in request
        assert "is not of type" in message
        assert error_type == "type"
        assert incorrect_type == str(type(request[field]).__name__)

    # Nothing added to DB
    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 0


def test_post_eligibility_400_invalid_enums(client, api_auth_token, test_db_session):
    request = base_request | {
        "eligibility_categories": ["abcdef", "ghij"],
        "eligibility_programs": ["klmno"],
    }
    response = client.post(
        "/v1/eligibility-screener", json=request, headers={"X-Auth": api_auth_token}
    )

    assert response.status_code == 400
    error_list = response.get_json()["errors"]
    # We expect the errors to be in a dict like:
    # {
    #   'field': 'eligibility_categories.0',
    #   'message': "'abcdef' is not one of ['pregnant', 'baby', 'guardian', 'loss']",
    #   'rule': ['pregnant', 'baby', 'guardian', 'loss'],
    #   'type': 'enum',
    #   'value': 'abcdef'
    # }
    assert len(error_list) == 3
    for error in error_list:
        field, message, error_type = error["field"], error["message"], error["type"]

        assert field in [
            "eligibility_categories.0",
            "eligibility_categories.1",
            "eligibility_programs.0",
        ]
        assert "is not one of" in message
        assert error_type == "enum"


def test_post_eligibility_401_unauthorized_token(client, api_auth_token, test_db_session):
    request = base_request | {}
    response = client.post(
        "/v1/eligibility-screener", json=request, headers={"X-Auth": "incorrect token"}
    )
    assert response.status_code == 401

    # Verify the error message
    assert (
        "The server could not verify that you are authorized to access the URL requested"
        in response.get_json()["message"]
    )
