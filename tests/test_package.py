import eveapi


def test_imports():
    should_exist = [
        "EVEAPIConnection",
        "Error",
        "AuthenticationError",
        "RequestError",
        "ServerError",
    ]
    top_level_objs = dir(eveapi)
    for obj in should_exist:
        assert obj in top_level_objs
