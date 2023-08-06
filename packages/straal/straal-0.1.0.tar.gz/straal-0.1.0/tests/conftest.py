import pytest


@pytest.fixture(scope="session")
def straal_base_url():
    return "https://straal/"


@pytest.fixture(autouse=True, scope="function")
def env_test_setup(monkeypatch, straal_base_url):
    """
    Makes sure tests will never fire requests to actual server
    """
    import straal

    straal.init("DUMMY_TEST_API_KEY", straal_base_url)


@pytest.fixture(scope="session")
def customer_json():
    return {
        "id": "xyz_123",
        "created_at": 1575376785,
        "email": "customer@example.net",
        "reference": "SOME_ID",
    }


@pytest.fixture(scope="session")
def customer_list_json():
    return {
        "page": 1,
        "per_page": 30,
        "total_count": 2,
        "data": [
            {
                "id": "xyz_123",
                "created_at": 1575376785,
                "email": "customer@example.net",
                "reference": "SOME_ID",
            },
            {
                "id": "abc_987",
                "created_at": 1575377785,
                "email": "other_customer@example.net",
                "reference": "SOME_OTHER_ID",
            },
        ],
    }
