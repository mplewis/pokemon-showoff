import pytest
import sure  # noqa


class FlaskTestConfig:
    DEBUG = False
    TESTING = True


@pytest.fixture
def client():
    import server
    server.app.config.from_object(FlaskTestConfig)
    return server.app.test_client()


def test_index():
    s = client()
    r = s.get('/')
    r.status_code.should.equal(200)


def test_post():
    s = client()
    r = s.post('/')
    r.status_code.should.equal(500)
