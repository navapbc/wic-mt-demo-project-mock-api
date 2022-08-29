import faker

fake = faker.Faker()


def test_post_eligibility_201(client):
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


def test_post_eligibility_400(client):
    request = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "phone_number": "this does not match the regex",
    }
    response = client.post("/v1/eligibility-screener", json=request)

    assert response.status_code == 400
    assert response.get_json()["detail"] is not None
