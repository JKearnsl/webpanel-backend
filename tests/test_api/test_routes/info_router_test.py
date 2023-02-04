from .auth_router_test import get_register_data
from ...conftest import client


def test_test_system_info():
    with client as init_client:
        user_data = get_register_data(init_client)
        response = init_client.get(
            "/api/v1/info/system",
            cookies=dict(
                access_token=user_data["access_token"],
                refresh_token=user_data["refresh_token"],
                session_id=user_data["session_id"]
            )
        )
        assert response.status_code == 200


def test_version():
    with client as init_client:
        response = init_client.get("/api/v1/info/version")
        assert response.status_code == 200
        assert response.json().get("version") is not None
