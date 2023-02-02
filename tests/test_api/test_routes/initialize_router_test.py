from ...conftest import client


def test_create_start_user():
    with client as init_client:
        response = init_client.put(
            "/api/v1/create_start_user",
            json=dict(
                username="admin",
                email="some@mail.com",
                password="admi3wef312n",
                role=3
            )
        )
        assert response.status_code == 201

        response = init_client.put(
            "/api/v1/create_start_user",
            json=dict(
                username="efwfewefwef",
                email="wefwefwef@gamail.com",
                password="admi3wef312n",
                role=3
            )
        )
        assert response.status_code == 404


def test_ping():
    with client as init_client:
        response = init_client.post("/api/v1/ping")
        assert response.status_code == 200
        assert response.json() == "pong"
