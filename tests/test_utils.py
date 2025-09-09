import random
import string


def random_string(length: int = 10) -> str:
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


def random_email() -> str:
    return f"{random_string(10)}@example.com"


def random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))


def assert_response_status(response, expected_status_code: int, message: str = None):
    try:
        response_data = response.json()
    except Exception:
        response_data = {}

    assert response.status_code == expected_status_code, (
        f"Expected status code {expected_status_code}, "
        f"but got {response.status_code}. "
        f"Response: {response.text}" + (f" {message}" if message else "")
    )
    return response_data


def assert_error_response(response, status_code: int, detail: str = None):
    response_data = assert_response_status(response, status_code)

    if status_code >= 400:
        assert "detail" in response_data, (
            f"Expected 'detail' in error response, got: {response_data}"
        )
        if detail is not None:
            assert response_data["detail"] == detail, (
                f"Expected error detail '{detail}', got '{response_data.get('detail')}'"
            )
