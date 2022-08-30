import faker

from api.db.models.eligibility_models import EligibilityScreener

fake = faker.Faker()


def test_post_eligibility_201(client, test_db_session):
    request = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "phone_number": "123-456-7890",
    }
    response = client.post("/v1/eligibility-screener", json=request)

    assert response.status_code == 201

    data = response.get_json()["data"]
    for k in request:
        assert data[k] == request[k]

    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 1
    assert results[0].eligibility_screener_id is not None
    assert results[0].created_at is not None
    assert results[0].updated_at is not None

    assert results[0].first_name == request["first_name"]
    assert results[0].last_name == request["last_name"]


def test_post_eligibility_400(client, test_db_session):
    request = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "phone_number": "this does not match the regex",
    }
    response = client.post("/v1/eligibility-screener", json=request)

    assert response.status_code == 400
    assert response.get_json()["detail"] is not None

    # Nothing added to DB
    results = test_db_session.query(EligibilityScreener).all()
    assert len(results) == 0
