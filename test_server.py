import pytest
import sure  # noqa
from StringIO import StringIO


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


def test_post_none():
    s = client()
    r = s.post('/')
    r.status_code.should.equal(400)
    r.data.should.equal('Expected 1 file, received 0 files.')


def test_post_one():
    s = client()
    data = {'upload_var': (StringIO('some save file'), 'pkmn.sav')}
    r = s.post('/', data=data)
    r.status_code.should.equal(200)
    r.data.should.equal('OK')


def test_post_two():
    s = client()
    files = {'save1': (StringIO('one save file'), 'file.sav'),
             'save2': (StringIO('another save file'), 'file.sav')}
    r = s.post('/', data=files)
    r.status_code.should.equal(400)
    r.data.should.equal('Expected 1 file, received 2 files.')
