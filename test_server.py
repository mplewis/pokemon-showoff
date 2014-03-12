import pytest
import sure  # noqa


@pytest.fixture
def client():
    import server
    server.app.config['DEBUG'] = False
    server.app.config['TESTING'] = True
    return server.app.test_client()


def test_index():
    s = client()
    r = s.get('/')
    r.status_code.should.equal(200)
